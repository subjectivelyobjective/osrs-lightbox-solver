# Copyright 2017 subjectivelyobjective.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import itertools

def char_combinations(str):
    char_combs = []
    str_list = list(str)
    for comb_len in range(0, len(str_list) + 1):
        for subset in itertools.combinations(str_list, comb_len):
            char_combs.append("".join(subset))
    return char_combs

def lists_xor(list1, list2):
    return [list1[i] ^ list2[i] for i in range(0, len(list1))]

def matrix_xor(matrix1, matrix2):
    return [lists_xor(matrix1[i], matrix2[i]) for i in range(0, len(matrix1))]

def unit_matrix(size):
    ones = [1 for i in range(0, size)]
    return [ones for i in range(0, size)]
