

base_link = 'https://www.sciencedirect.com/search?qs=sers&show=100'
elsevier_link_over_hundred = 'https://www.sciencedirect.com/search?qs=sers&show=100&offset=100'
class Paper:
    def __init__(self):
        pass


class Author:
    def __init__(self):
        self.first_name = ''
        self.second_name = ''
        self.email = ''
        self.paper_title = ''  # tag == title
        self.url = ''  # tag == a, class == ArticleIdentifierLinks
        self.affiliation = ''  # tag == div, class == affiliation


if __name__ == '__main__':

    pass
