from services.ai_excel_generators.comp_report import generate_excel_report
from services.generate_excel import open_excel


def test_ai_gen_comp_report():
    data = {
    '1': {
        '6': {'SF194DB': ['Cheesecake - Vanilla Bean 2"',
                           [398, 532, 880],
                           [28385, 40672, 68585]]},
        '19': {'MIDI190': ['Flourless - Chocolate MIDI',
                            [588, 561, 758],
                            [24631, 25148, 34722]],
               'MIDI194': ['Cheesecake - Vanilla Bean MIDI',
                            [777, 754, 942],
                            [32549, 33796, 43144]],
               'ZSF202D': ['DO NOT USE Explosion - Chocolate 3"',
                            [206, 98, 0],
                            [12570, 6386, 0]]},
        '3': {'SF184D': ['Mousse - Triple Chocolate 3"',
                          [180, 228, 210],
                          [11502, 15567, 14670]],
              'SF189D': ['Layer - Carrot 3"',
                          [170, 142, 144],
                          [10863, 9214, 9565]]},
    },
    '2': {
        '350': {'ABE350': ["Vegan Square Cake - ABE'S Corn Bread",
                            [60, 110, 140],
                            [1154, 2194, 2930]]},
    },
}

    wb = generate_excel_report(data)
    open_excel(wb)