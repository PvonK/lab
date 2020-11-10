import os


class HtmlCreator():

    def __init__(self):
        self.output = '<!DOCTYPE html>\n<html>'
        self.form_list = []

    def addLine(self):
        self.output += '<br>\n'

    def createHiperlink(self, link, text):
        self.output += '<a href="{}">{}</a>'.format(link, text)

    def createForm(self, action, button_text, breaks=False):

        if breaks:
            br = '<br>'
        else:
            br = ''

        self.output += '<form action="{}"><input type="submit" value="{}">\n'\
                       .format(action, button_text)

        self.output += br

        self.output += br.join(self.form_list)

        self.output += '</form>'

        self.form_list = []

    def createTextInput(self, typ, text, form_id, name, value='', minimum='', step=''):

        output = ''

        output += '<label for="{}">{}</label>'.format(form_id, text)
        output += '''<input type="{}" min="{}" step="{}"
                     id="{}"
                     name="{}"
                     value="{}">'''\
                         .format(typ, minimum, step, form_id, name, value)

        self.form_list.append(output)

    def createRadioInput(self, form_id, name, value, text):

        output = ''

        output += '''<input type="radio"
                      id="{}"
                      name="{}"
                      value="{}">'''.format(form_id, name, value)

        output += '<label for="{}">{}</label>'.format(form_id, text)

        self.form_list.append(output)

    def centerText(self, text):
        return '<center>{}</center>'.format(text)

    def title(self, text, number):
        self.output += '<h{}>{}</h{}>'.format(number, text, number)

    def getHtml(self):
        self.output += '</html>'
        return self.output


def ls_html(page):

    if not page.endswith("/"):
        page += "/"
    folderNameIndex = page.rfind("/", 0, -1)
    folderName = page[folderNameIndex:]

    h = HtmlCreator()
    h.title(h.centerText(folderName), 3)

    files = os.listdir(page)
    for data in files:

        h.createHiperlink(page + data, data)
        h.addLine()

    html_code = h.getHtml().encode()
    http_header = b"HTTP/1.1 200 OK\nContent-Type: text/html\nContent-"
    http_header += b"Length: " + str(len(html_code)).encode() + b"\n\n"

    return http_header + html_code


"""
<form action="{}">
<input type="submit" value="{}">

<input type="radio" id="R" name="filter" value="red">
<label for="red">Red</label>

    <input type="radio" id="G" name="filter" value="green">
    <label for="green">Green</label>

    <input type="radio" id="B" name="filter" value="blue">
    <label for="blue">Blue</label>

    <input type="radio" id="W" name="filter" value="W">
    <label for="W">Black & White</label>

    <label for="scale">scale:</label>
    <input type="text" id="scale" name="scale" value="1">
</form>
"""
