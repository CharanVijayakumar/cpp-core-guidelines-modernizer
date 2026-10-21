"""Non-destructive clang-tidy orchestration for legacy C++ projects.

This is a reconstructed implementation inspired by the author's dissertation,
not a recovery of the original source code.
"""
import argparse
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

EXTENSIONS = {'.cpp', '.cc', '.cxx', '.hpp', '.hh', '.h'}
DIAGNOSTIC = re.compile(r'^(.*?):(\d+):(\d+):\s+(?:warning|error):\s+(.*?)\s+\[([^]]+)\]\s*$')
DEFAULT_CHECKS = '-*,cppcoreguidelines-*,modernize-use-nullptr,modernize-use-using'


def sources(root: Path):
    if root.is_file():
        if root.suffix not in EXTENSIONS:
            raise ValueError(f'Unsupported source extension: {root}')
        return [root]
    return sorted(p for p in root.rglob('*') if p.is_file() and p.suffix in EXTENSIONS and not any(x in {'build', '.git', 'annotated', 'corrected'} for x in p.parts))


def parse_diagnostics(output: str):
    findings = []
    for line in output.splitlines():
        match = DIAGNOSTIC.match(line.strip())
        if match:
            path, lineno, col, message, check = match.groups()
            findings.append({'file': path, 'line': int(lineno), 'column': int(col), 'message': message, 'check': check})
    return findings


def annotate(source: str, findings):
    lines = source.splitlines(keepends=True)
    grouped = {}
    for finding in findings:
        grouped.setdefault(finding['line'], []).append(finding)
    result = []
    for index, line in enumerate(lines, start=1):
        for finding in grouped.get(index, []):
            msg = finding['message'].replace('\n', ' ').replace('*/', '* /')
            result.append(f"// clang-tidy [{finding['check']}]: {msg}\n")
        result.append(line)
    return ''.join(result)


def run_tidy(path, tidy, checks, compile_db=None, fix=False):
    command = [tidy, str(path), f'-checks={checks}', '--quiet']
    if compile_db:
        command += ['-p', str(compile_db)]
    else:
        command += ['--', '-std=c++17']
    if fix:
        command.insert(2, '-fix')
    return subprocess.run(command, text=True, capture_output=True, check=False)


def main(argv=None):
    parser = argparse.ArgumentParser(description='Annotate and selectively modernize legacy C++ files using clang-tidy.')
    parser.add_argument('input', type=Path, help='C++ source file or directory')
    parser.add_argument('--output', type=Path, default=Path('output'))
    parser.add_argument('--clang-tidy', default='clang-tidy')
    parser.add_argument('--checks', default=DEFAULT_CHECKS)
    parser.add_argument('--compile-db', type=Path, help='Directory containing compile_commands.json (single-file analysis only in this prototype)')
    args = parser.parse_args(argv)
    root = args.input.resolve()
    if not root.exists():
        parser.error('Input path does not exist')
    if args.compile_db and root.is_dir():
        parser.error('--compile-db with directory mode is not supported in this prototype')
    if not shutil.which(args.clang_tidy):
        parser.error(f'Cannot find clang-tidy executable: {args.clang_tidy}')
    output = args.output.resolve()
    if output == root or (root.is_dir() and root in output.parents):
        parser.error('Output must be outside the input tree')
    try:
        files = sources(root)
    except ValueError as exc:
        parser.error(str(exc))
    if not files:
        parser.error('No supported C++ files found')
    records = []
    for src in files:
        relative = src.relative_to(root) if root.is_dir() else Path(src.name)
        annotated = output / 'annotated' / relative
        corrected = output / 'corrected' / relative
        annotated.parent.mkdir(parents=True, exist_ok=True)
        corrected.parent.mkdir(parents=True, exist_ok=True)
        original = src.read_text(encoding='utf-8')
        analysis = run_tidy(src, args.clang_tidy, args.checks, args.compile_db)
        findings = parse_diagnostics(analysis.stdout + '\n' + analysis.stderr)
        annotated.write_text(annotate(original, findings), encoding='utf-8')
        corrected.write_text(original, encoding='utf-8')
        if args.compile_db:
            fix_status = 'skipped: compilation database paths require remapping'
        else:
            fix_run = run_tidy(corrected, args.clang_tidy, args.checks, fix=True)
            fix_status = 'attempted' if fix_run.returncode == 0 else f'clang-tidy exit {fix_run.returncode}'
        records.append({'input': str(src), 'annotated': str(annotated), 'corrected': str(corrected), 'findings': findings, 'analysis_exit_code': analysis.returncode, 'fix_status': fix_status})
    output.mkdir(parents=True, exist_ok=True)
    (output / 'report.json').write_text(json.dumps({'files': records}, indent=2), encoding='utf-8')
    print(f'Processed {len(records)} file(s). Outputs: {output}')
    if any(item['analysis_exit_code'] != 0 for item in records):
        print('Warning: one or more clang-tidy analyses returned nonzero; inspect report.json', file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
