from scripts.webdriver import get_report


def run(*args):
    if args:
        week = f"2022W{args[0]}5"
    else:
        week = None
    print(get_report(week=False, week_number=week, driver=True, sleep=5, headless=True))



