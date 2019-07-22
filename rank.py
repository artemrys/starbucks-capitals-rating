import csv
import collections


CityStarbucks = collections.namedtuple(
    "CityStarbucks", ["country", "capital", "n_starbucks"]
)


def read_data():
    result = []
    with open("data.csv", "r") as f:
        reader = csv.reader(f, delimiter=",", quotechar='"')
        for row in reader:
            result.append(
                CityStarbucks._make(
                    [
                        row[0],
                        row[1],
                        int(row[2]),
                    ]
                )
            )
    return result


def calculcate_zeros(data):
    return len(
        [
            elem for elem in data
            if elem.n_starbucks != 0
        ]
    )


def top(data, n=30):
    sorted_data = sorted(
        data, key=lambda e: e.n_starbucks, reverse=True
    )
    return [elem for elem in sorted_data][:n]


def main():
    data = read_data()
    print(calculcate_zeros(data))
    for elem in top(data):
        print(elem)


if __name__ == "__main__":
    main()
