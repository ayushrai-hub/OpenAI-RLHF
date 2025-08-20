

include <iostream>

int main() {
    std::cout << "Hello, World!" << std::endl;
    return 0;
}
EOF

# Compile the C++ file
g++ hello.cpp -o hello

# Run the compiled program
./hello