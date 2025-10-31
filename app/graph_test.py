from graph_structure import Link
def main():
    test = Link(5,True, "The quick brown fox jumped over the lazy dog")
    print(test.window_check("fox"))

if __name__ == "__main__":
    main()