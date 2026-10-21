#include <iostream>
#include <cstddef>
int main() {
    int* value = new int(42);
    if (value != NULL) {
        std::cout << *value << '\n';
    }
    delete value;
    return 0;
}
