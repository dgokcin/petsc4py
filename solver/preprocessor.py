import argparse
import pandas as pd
import json
import os


def main(command_line_arguments):
    matrix = Matrix(command_line_arguments['matrix'])
    matrix.update_json_file()


class Matrix:
    def __init__(self, file_name):
        self.__json_file = file_name
        with open(self.__json_file, 'r') as json_file:
            self.__metadata = json.load(json_file)

        self.__matrix_file = self.__metadata['group'] + '/' + self.__metadata['name'] + '/' + os.path.splitext(os.path.basename(self.__json_file))[
            0] + '.mtx'
        self.__matrix_name = self.__metadata['name']

        # Read metadata in MM format: row, column, entries
        self.__rows = int(self.__metadata['num_rows'])
        self.__columns = int(self.__metadata['num_cols'])
        self.__entries = int(self.__metadata['nonzeros'])

        self.__sparsity = self.__entries / (self.__rows * self.__columns)

        # Calculate Bandwidth
        non_zero_values = pd.read_csv(self.__matrix_file, comment='%', delim_whitespace=True, skiprows=1)
        non_zero_values.columns = ['row', 'column', 'value']
        non_zero_values['bandwidth'] = pd.Series.abs(non_zero_values['row'] - non_zero_values['column'])
        self.__bandwidth = non_zero_values['bandwidth'].max()

    def get_matrix_name(self):
        return self.__matrix_name

    def get_rows(self):
        return self.__rows

    def get_columns(self):
        return self.__columns

    def get_entries(self):
        return self.__entries

    def get_bandwidth(self):
        return self.__bandwidth

    def __str__(self):
        return "Matrix_name: " + str(self.__matrix_name) + "\nRows: " + str(self.__rows) + "\nColumns: " + \
               str(self.__columns) + "\nEntries: " + str(self.__entries) + "\nBandwidth: " + str(self.get_bandwidth())

    def update_json_file(self):
        self.__metadata.update({"bandwidth": str(self.__bandwidth), "sparsity": str(self.__sparsity)})
        with open(self.__json_file, 'w') as f:
            json.dump(self.__metadata, f, indent=4)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Sparse Matrix Logger')
    parser.add_argument('-m', '--matrix', help='Matrix file (JSON)', required=True)
    args = vars(parser.parse_args())
    main(args)
