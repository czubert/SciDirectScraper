import re


class Author:
    def __init__(self):
        self.first_name = ''
        self.surname = ''
        self.email = ''
        self.affiliation = ''

    def get_author_meta(self, data):
        try:
            for mail in data.find_all_next('div', {'class': 'e-address'}):
                email = mail.find('a').get('href')
                if re.match(r'.+@.+\..+', email):
                    self.email = re.search(r'(?<=mailto:)(.+)@(.+)\.(.+)', email).group()
        except Exception as e:
            print(f'Getting e-mail failed! Reason?: {e}')
        try:
            for name in data.find('span', {'class': "given-name"}):
                self.first_name = name
        except Exception as e:
            print(f'Getting given name failed! Reason?: {e}')
        try:
            for surname in data.find('span', {'class': "surname"}):
                self.surname = surname
        except Exception as e:
            print(f'Getting surname failed! Reason?: {e}')
