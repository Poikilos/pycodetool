# -*- coding: utf-8 -*-
"""
Created on Tue Jul 19 18:29:39 2022

@author: Jake "Poikilos" Gustafson
"""

import unittest
import sys
import os

my_dir = os.path.dirname(os.path.abspath(__file__))
module_dir = os.path.dirname(my_dir)
repo_dir = os.path.dirname(module_dir)

if __name__ == "__main__":
    sys.path.insert(0, repo_dir)

from pycodetool import (
    echo0,
    echo1,
    echo2,
    set_verbosity,
)

from pycodetool.parsing import (
    quoted_slices,
    get_quoted_slices_error,
    which_slice,
    in_any_slice,
    END_BEFORE_QUOTE_ERR,
    explode_unquoted,
    find_unquoted_not_commented_not_parenthetical,
    find_unquoted_even_commented,
    find_unquoted_not_commented,
    assertEqual,  # This is a special one with custom output.
    AbstractFn,
    slice_is_space,
    isnumber,
    explode_unquoted,
)



from pycodetool.fxshim import (
    optionalD,
)


class TestParsing(unittest.TestCase):

    def assertAllEqual(self, list1, list2, tbs=None):
        '''
        [copied from pycodetools.parsing by author]
        '''
        if len(list1) != len(list2):
            echo0("The lists are not the same length: list1={}"
                  " and list2={}".format(list1, list2))
            self.assertEqual(len(list1), len(list2))
        for i in range(len(list1)):
            try:
                self.assertEqual(list1[i], list2[i])
            except AssertionError as ex:
                if tbs is not None:
                    echo0("reason string (tbs): " + tbs)
                raise ex

    def test_quoted_slices(self):
        set_verbosity(1)
        subject = '"example\'s param1", \'"param 2"\', param3'
        #                     0                 18
        #                                        19             31
        #                                                        32
        # ^ Note that the backslash is skipped in these indices.
        good_indices = [
            0,
            subject.find('\'"param 2'),
        ]
        good_ends = [
            subject.find(', \'"param 2'),
            subject.find(', param3'),
        ]
        # ^ param3 is NOT part of quoted_slices, and
        #   quoted_slices is NOT the same as explode_strings
        #   (quoted_slices does not look for delimiters).
        good_pairs = []
        for i in range(len(good_indices)):
            good_pairs.append((good_indices[i], good_ends[i]))
        results = quoted_slices(subject)

        self.assertEqual(
            len(results),
            2
        )

        self.assertEqual(
            results,
            good_pairs
        )

        parts = []
        for pair in results:
            parts.append(subject[pair[0]:pair[1]])

        self.assertEqual(
            parts,
            ['"example\'s param1"', '\'"param 2"\'']
        )

    def test_quoted_slices_comment_exclusion(self):
        set_verbosity(1)
        subject = 'x = "a" + (i + a) + "a"  // "a"'
        slices = quoted_slices(subject, comment_delimiters=["//", "#"])
        self.assertEqual(
            len(slices),
            2
        )

        subject = 'x = "a" + (i + a) + "a" # "a"'
        #          0   4 6             20
        #                                22  26
        #                                      28
        # ^ Note the quotes 26 and 28 should be ignored since commented.
        slices = quoted_slices(subject, comment_delimiters=["//", "#"])
        self.assertEqual(
            len(slices),
            2
        )
        parts = []
        for params in slices:
            parts.append(subject[params[0]:params[1]])
        self.assertEqual(parts, ['"a"', '"a"'])

    def test_quoted_slices_start(self):
        echo0("* test quoted_slices...")
        # intentionally botch the results by starting after the opening quote:
        test_s = 'x = "a" + (i + a) + "a" # "b"'
        goodIs = [(6, 21), (22, 27)]
        assertEqual(test_s[goodIs[0][0]:goodIs[0][1]], '" + (i + a) + "',
                    tbs="The silent degradation test itself is wrong.")
        assertEqual(test_s[goodIs[1][0]:goodIs[1][1]], '" # "',
                    tbs="The silent degradation test itself is wrong.")
        gotIs = quoted_slices(test_s, start=6)
        self.assertAllEqual(
            goodIs,
            gotIs,
            tbs=("quoted slices {} should silently degrade to {}"
                 "".format(gotIs, goodIs)),
        )
        assertEqual(get_quoted_slices_error(), END_BEFORE_QUOTE_ERR)
        echo0("^ TEST: An unterminated quote is expected since start=6"
              " (if it warned correctly, it PASSED)")

        test_s = 'x = "a" + (i + a) + "a" # "c"'
        goodIs = [(4, 7), (20, 23)]
        assertEqual(test_s[goodIs[0][0]:goodIs[0][1]], '"a"',
                    tbs="The test itself is wrong.")
        assertEqual(test_s[goodIs[1][0]:goodIs[1][1]], '"a"',
                    tbs="The test itself is wrong.")
        gotIs = quoted_slices(test_s)
        self.assertAllEqual(goodIs, gotIs, tbs=("quoted slices {} should be {}"
                                           "".format(gotIs, goodIs)))
        assertEqual(get_quoted_slices_error(), None)


        goodIs = [(4, 6), (20, 22)]

        w_slice = which_slice(21, goodIs)
        assertEqual(w_slice, 1)
        a_slice = in_any_slice(21, goodIs)
        assertEqual(a_slice, True)

        w_slice = which_slice(5, goodIs)
        assertEqual(w_slice, 0)
        a_slice = in_any_slice(5, goodIs)
        assertEqual(a_slice, True)

        w_slice = which_slice(6, goodIs)
        assertEqual(w_slice, -1)
        a_slice = in_any_slice(6, goodIs)
        assertEqual(a_slice, False)


        assertEqual(optionalD(11.123456, 5).format(11.123456), '11.12346')
        assertEqual(optionalD(11.12345, 5).format(11.12345), '11.12345')
        assertEqual(optionalD(11.1234, 5).format(11.1234), '11.1234')
        assertEqual(optionalD(11, 5).format(11), '11')

    def test_explode_strings(self):
        set_verbosity(1)
        subject = '"example\'s param1", \'"param 2"\', param3'
        good_indices = [
            0,
            subject.find(' "param 2'),
            subject.find(' param3'),
        ]
        good_ends = [
            good_indices[1]-1,
            good_indices[2]-1,
            len(subject),
        ]

        echo0("good_indices={}".format(good_indices))

        good_params = ['"example\'s param1"', '\'"param 2"\'', "param3"]

        results = explode_unquoted(subject, ",")

        self.assertEqual(
            results,
            good_params
        )

    def test_explode_strings_and_indices(self):
        set_verbosity(1)
        subject = '"example\'s param1",, \'"param 3"\', param4'
        good_params = ['"example\'s param1"', "", '\'"param 3"\'', "param4"]
        good_indices = [
            0,
            subject.find(",,")+1, # +1 for START of element 1
            subject.find(' \'"param 3'),
            subject.find(' param4'),
        ]
        good_ends = [
            good_indices[1]-1,
            good_indices[2]-1,
            good_indices[3]-1,
            len(subject),
        ]

        echo0("good_indices={}".format(good_indices))

        good_pairs = []
        for i in range(len(good_params)):
            good_pairs.append((good_params[i], good_indices[i], good_ends[i]))

        results = explode_unquoted(subject, ",", get_str_i_tuple=True)

        self.assertEqual(
            results,
            good_pairs
        )

    def test_find_unquoted_not_commented_not_parenthetical(self):
        echo0("* find_unquoted_not_commented_not_parenthetical...")
        found = find_unquoted_not_commented_not_parenthetical(
            "x = (i + a) + b # a",
            "a",
        )
        assertEqual(found, -1)

        good_i = 14
        found = find_unquoted_not_commented_not_parenthetical(
            "x = (i + a) + a # a",
            #              ^ for the test, good_s must be at good_i
            "a",
        )
        assertEqual(found, good_i)

        good_i = 14
        found = find_unquoted_not_commented_not_parenthetical(
            "x = (i + a) + a # a",
            #              ^ for the test, good_s must be at good_i
            "a",
            step=-1,  # Ensure a commented good_s is skipped by going in reverse
        )
        assertEqual(found, good_i)

        set_verbosity(1)

        good_i = 20
        found = find_unquoted_not_commented_not_parenthetical(
            "x = 'a' + (i + a) + a # a",
            #                    ^ for the test, this index must match good_i
            "a",
        )
        assertEqual(found, good_i, tbs=("find a non-quoted non-parenthetical"
                                        " string after other matches that are"))

        good_i = 20
        good_s = "a"
        test_s = 'x = "a" + (i + a) + a # a'
        #                             ^ for the test, good_s must be at good_i
        assertEqual(good_s, test_s[good_i:good_i+len(good_s)],
                    tbs="The test itself is wrong: good_s is not at good_i")
        found = find_unquoted_not_commented_not_parenthetical(
            test_s,
            good_s,
        )
        assertEqual(
            found,
            good_i,
            tbs="finding a non-quoted non-parenthetical string",
        )

        test_s = 'x = \\"a" + (i + a) + \"a\" # a'
        good_i = -1
        good_s = "a"
        # assertEqual(good_s, test_s[good_i:good_i+len(good_s)],
        #             tbs="The test itself is wrong: good_s is not at good_i")
        # ^ don't check since good_i is -1 (not found is correct)
        found = find_unquoted_not_commented_not_parenthetical(
            test_s,
            good_s,
        )
        assertEqual(found, good_i, tbs=("should find nothing since a backslash"
                                        " outside of quotes doesn't count"))

        test_s = 'x = "\\"" + a + (i + a) + \"a\" # a'
        good_i = 11
        good_s = "a"
        assertEqual(good_s, test_s[good_i:good_i+len(good_s)],
                    tbs="The test itself is wrong: good_s is not at good_i")
        found = find_unquoted_not_commented_not_parenthetical(
            test_s,
            good_s,
        )
        assertEqual(found, good_i, tbs="finding the first escaped string")

        test_s = 'x = \'\\\'\' + a + (i + a) + \"a\" # a'
        good_i = 11
        good_s = "a"
        assertEqual(good_s, test_s[good_i:good_i+len(good_s)],
                    tbs="The test itself is wrong: good_s is not at good_i")
        found = find_unquoted_not_commented_not_parenthetical(
            test_s,
            good_s,
        )
        assertEqual(found, good_i, tbs=("finding the first escaped string with"
                                        " an escaped quote"))

        test_s = 'x = \'\\\'a\' + (i + a) + \"a\" # a'
        good_i = 17
        good_s = "a"
        assertEqual(good_s, test_s[good_i:good_i+len(good_s)],
                    tbs="The test itself is wrong: good_s is not at good_i")
        found = find_unquoted_not_commented_not_parenthetical(
            test_s,
            good_s,
            step=-1,
        )
        assertEqual(found, good_i, tbs="finding the last escaped string")

        # intentionally provide bad syntax to ensure the escape character is
        # ignored when not in quotes:
        test_s = 'x = \\"a" + (i + a) + \\"a\" # a'
        good_i = 6
        good_s = "a"
        assertEqual(good_s, test_s[good_i:good_i+len(good_s)],
                    tbs="The test itself is wrong: good_s is not at good_i")
        found = find_unquoted_not_commented_not_parenthetical(
            test_s,
            good_s,
            step=-1,
        )
        assertEqual(found, good_i, tbs=("finding the last escaped string after"
                                        " another escaped string"))

    def test_parse_function(self):
        fnStr0 = "    mysqli_connect(\"localhost\", 'dbn', 'pwd', 'dbn')"
        # ^ use 'dbn' twice for testing dbname, which is
        #   sometimes the same as the dbuser.
        fnStr1 = "    mysqli_connect(\"localhost\", $dbuser, 'pwd', 'dbn')"
        abstractfn = AbstractFn(fnStr0)
        self.assertEqual(abstractfn.to_string(), fnStr0)
        abstractfn.set_param(1, " $dbuser")
        self.assertEqual(abstractfn.to_string(), fnStr1)

    '''
    def test_change_function_param(self):
        self.assertEqual(
            replace_param_if(fnStr0, 1, " $dbuser", "'dbn'"),
            fnStr1
        )
        self.assertEqual(
            replace_param_if(fnStr0, 1, " $dbuser", "dbn"),
            fnStr1,
            find_if_any_quotes=True,
        )
        self.assertEqual(
            replace_param_if(fnStr0, 1, " $dbuser", "dbn"),
            fnStr0
        ) # It shouldn't change in this case.
    '''

    def test_slice_is_space(self):
        set_verbosity(2)
        self.assertEqual(slice_is_space("abc ", -1, None), True)
        self.assertEqual(slice_is_space("abc", -1, None), False)
        self.assertEqual(slice_is_space("abc ", -2, None), False)
        self.assertEqual(slice_is_space("abc", 3, None), False)
        self.assertEqual(slice_is_space("abc ", 3, None), True)
        self.assertEqual(slice_is_space("abc d", 3, 4), True)

    def test_isnumber(self):
        c_suffixes = ["f"]
        self.assertEqual(isnumber("4.0f"), False)
        self.assertEqual(isnumber("4.0f", suffixes=c_suffixes), True)
        self.assertEqual(isnumber("4.0"), True)
        self.assertEqual(isnumber("4.0"), True)
        self.assertEqual(isnumber("4"), True)
        self.assertEqual(isnumber("4f"), False)
        self.assertEqual(isnumber("4f", suffixes=c_suffixes), True)

    def test_find_unquoted_even_commented(self):
        sample = '<a href="#b" #a #b>'
        tag_i = find_unquoted_even_commented(sample, "b")
        self.assertEqual(tag_i, 17)  # 17 for 2nd b, not quoted one
        self.assertEqual(sample[tag_i-1:tag_i+2], "#b>")

    def test_find_unquoted_not_commented(self):
        sample = '<a href="#b" #a #b>'
        tag_i = find_unquoted_not_commented(sample, "b")
        self.assertEqual(tag_i, -1)  # 1st b is quoted, next is comment


    def test_explode_unquoted__ignore_quoted_delimiters(self):
        '''
        test_explode_unquoted__ methods test parsing assignment
        operations (attributes) inside of an HTML opening tag.
        - allow_escaping_quotes=False since in HTML, "&quot;" is the
          correct way to escape quotes.
        '''

        sample = 'a href="b c" d e'
        # echo0()
        # echo0("0. Ignore (only) quoted delimiters:")
        parts = explode_unquoted(sample, " ", min_indent="  ",
                                 allow_escaping_quotes=False)
        echo0("  parts={}".format(parts))
        self.assertEqual(len(parts), 4)
        self.assertEqual(parts[0], "a")
        self.assertEqual(parts[1], 'href="b c"')
        self.assertEqual(parts[2], "d")
        self.assertEqual(parts[3], "e")

    def test_explode_unquoted__do_not_allow_commented(self):
        sample = 'a href="#b c" #d #e'
        set_verbosity(2)
        # echo0()
        # echo0("1. Do not allow commented:")
        '''
        allow_commented=False is not the correct way to parse HTML
        since '#' is not a comment mark in HTML, but this will test the
        explode_unquoted allow_commented=False feature in a way that is
        not HTML-specific to test the case:
        '''
        parts = explode_unquoted(sample, " ", allow_commented=False,
                                 min_indent="  ",
                                 allow_escaping_quotes=False)
        echo0("  parts={}".format(parts))
        self.assertEqual(len(parts), 2)
        self.assertEqual(parts[0], "a")
        self.assertEqual(parts[1], 'href="#b c"')

    def test_explode_unquoted__allow_commented(self):
        sample = 'a href="#b c" #d #e'

        # echo0()
        # echo0("2. Allow commented:")
        parts = explode_unquoted(sample, " ", allow_commented=True,
                                 min_indent="  ",
                                 allow_escaping_quotes=False)
        echo0("  parts={}".format(parts))
        self.assertEqual(parts[0], "a")
        self.assertEqual(parts[1], 'href="#b c"')
        self.assertEqual(parts[2], "#d")
        self.assertEqual(parts[3], "#e")

    def test_explode_unquoted__allow_commented_and_other_quote_marks(self):
        sample = 'a href="#b c" \'#d #e\''
        # echo0()
        # echo0("3. Allow commented, only quotes are '\"':")
        parts = explode_unquoted(sample, " ", quote_marks='"',
                                 allow_commented=True,
                                 min_indent="  ",
                                 allow_escaping_quotes=False)
        echo0("  parts={}".format(parts))
        self.assertEqual(parts[0], "a")
        self.assertEqual(parts[1], 'href="#b c"')
        self.assertEqual(parts[2], "'#d")
        self.assertEqual(parts[3], "#e'")


if __name__ == "__main__":
    testcase = TestParsing()
    # testcase.test_find_unquoted_even_commented()
    # testcase.test_find_unquoted_not_commented()
    # sys.exit(1)  # debug only

    for name in dir(testcase):
        if name.startswith("test"):
            echo0()
            echo0("Running {}...".format(name))
            fn = getattr(testcase, name)
            fn()  # Look at def test_* for the code if tracebacks start here
