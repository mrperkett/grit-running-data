import pandas as pd

from parsing import parse_grit_html
from utils import obfuscate_html_table


class TestObfuscation:
    two_entry_table_html_str = """<table class="results results--rowHover" id="resultsTable">
    <thead>
        <tr>
            <th>Place</th>
            <th>Bib</th>
            <th>Name</th>
            <th>Gender</th>
            <th>City</th>
            <th>State</th>
            <th>Country</th>
            <th>Clock<br>Time</th>
            <th>Chip<br>Time</th>
            <th class="noSort">Distance in Miles</th>
            <th class="noSort">Progress</th>
            <th class="noSort">Elevation Gain</th>
            <th>Pace</th>
            <th>Age</th>
            <th>Age<br>Percentage<i class="icon icon-info tippy-tip" tabindex="0"
                    data-tippy-content="This shows how well you performed based on your age.  Higher numbers are better, with 100% being the best."
                    aria-expanded="false"></i></th>
            <th class="noSort">Run Crew Name</th>
        </tr>
    </thead>
    <tbody>
        <tr data-result-url="/Race/Results/90618/IndividualResult/BkfK?resultSetId=459362#U89338374">
            <td class="place">1</td>
            <td class="bib">2533</td>
            <td class="ta-left">
                <div class="participantName">
                    <div class="participantName__image">
                        <div class="rsuCircleImg rsuCircleImg--xs rsuCircleImg--firstChar"><span>R</span></div>
                    </div>
                    <div class="participantName__name">
                        <div class="participantName__name__firstName">Matthew</div>
                        <div class="participantName__name__lastName">Perkett</div>
                    </div>
                </div>
            </td>
            <td>M</td>
            <td>Golden</td>
            <td>CO</td>
            <td>US</td>
            <td class="time">34:42:29</td>
            <td class="time"></td>
            <td>259.06</td>
            <td>64.8%</td>
            <td>396ft (120.7m)</td>
            <td class="time">8:02</td>
            <td>36</td>
            <td>96.7</td>
            <td></td>
        </tr>
        <tr data-result-url="/Race/Results/90618/IndividualResult/BkfK?resultSetId=459362#U89338374">
            <td class="place">1</td>
            <td class="bib">2533</td>
            <td class="ta-left">
                <div class="participantName">
                    <div class="participantName__image">
                        <div class="rsuCircleImg rsuCircleImg--xs rsuCircleImg--firstChar"><span>R</span></div>
                    </div>
                    <div class="participantName__name">
                        <div class="participantName__name__firstName">Steve</div>
                        <div class="participantName__name__lastName">Prefontaine</div>
                    </div>
                </div>
            </td>
            <td>M</td>
            <td>Eugene</td>
            <td>OR</td>
            <td>US</td>
            <td class="time">17:43:49</td>
            <td class="time"></td>
            <td>417.0</td>
            <td>51.0%</td>
            <td>25,000ft (7620.0m)</td>
            <td class="time">5:42</td>
            <td>73</td>
            <td>99.9</td>
            <td>Ducks</td>
        </tr>
    </tbody>
</table>
"""

    def test_obfuscate_html_table(self):
        """
        Verify that the first and last names are properly obfuscated
        """
        html_text = self.two_entry_table_html_str
        obfuscated_html_text = obfuscate_html_table(html_text)

        # parse html strings into dataframes
        df_orig = parse_grit_html(html_text)
        df_new = parse_grit_html(obfuscated_html_text)

        # check basic properties of df_orig to ensure things are as expected
        assert len(df_orig.columns) == 16
        assert "name" in df_orig.columns
        assert len(df_orig) == 2

        # verify that all columns other than "name" are unchanged
        columns = [column for column in df_orig.columns if column != "name"]
        pd.testing.assert_frame_equal(df_orig[columns], df_new[columns])

        # verify that no first or last names are in the obfuscated HTML
        all_names = set([name for full_name in df_new["name"] for name in full_name.split()])
        orig_names = set(["Matthew", "Perkett", "Steve", "Prefontaine"])
        assert all_names & orig_names == set()
