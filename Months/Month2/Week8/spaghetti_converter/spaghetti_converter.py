def main():
    spaghetti = input()
    try:
        spaghetti = int(spaghetti)
    except ValueError:
        try:
            spaghetti = float(spaghetti)
        except ValueError:
            print("Invalid input: Not a number.")
            exit()
    print('Data type  =: ', type(spaghetti))
    print('Data value =: ', spaghetti)

if __name__ == "__main__":
    main()