// ideal_completion.cpp

#include <iostream>
#include <stdexcept>

namespace someone_else {

template <typename T, size_t maxCapacity = 10, bool dynamicFlag = false>
struct dynamic_stack_array {
private:
    T* data;
    size_t current_size;
    size_t capacity;
    bool is_dynamic;

    void resize() {
        size_t new_capacity = capacity * 2;
        T* new_data = new T[new_capacity];
        for (size_t i = 0; i < current_size; ++i) {
            new_data[i] = data[i];
        }
        delete[] data;
        data = new_data;
        capacity = new_capacity;
    }

public:
    // Default constructor using template arguments
    dynamic_stack_array()
        : data(new T[maxCapacity]), current_size(0), capacity(maxCapacity), is_dynamic(dynamicFlag) {}

    // Parameterized constructor to override template arguments
    dynamic_stack_array(size_t customCapacity, bool customDynamicFlag)
        : data(new T[customCapacity]), current_size(0), capacity(customCapacity), is_dynamic(customDynamicFlag) {}

    ~dynamic_stack_array() {
        delete[] data;
    }

    void push_back(const T& element) {
        if (current_size >= capacity) {
            if (is_dynamic) {
                resize();
            } else {
                throw std::overflow_error("Array capacity exceeded.");
            }
        }
        data[current_size++] = element;
    }

    void clear() {
        current_size = 0;
    }

    size_t size() const {
        return current_size;
    }

    T& operator[](size_t index) {
        if (index >= current_size) {
            throw std::out_of_range("Index out of range.");
        }
        return data[index];
    }

    const T& operator[](size_t index) const {
        if (index >= current_size) {
            throw std::out_of_range("Index out of range.");
        }
        return data[index];
    }
};

} // namespace someone_else
