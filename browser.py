#!/usr/bin/env python

import urllib
from Tkinter import *

url1 = "http://studentnet.cs.manchester.ac.uk/ugt/COMP18112/page1.html"
url2 = "http://studentnet.cs.manchester.ac.uk/ugt/COMP18112/page2.html"
url3 = "http://studentnet.cs.manchester.ac.uk/ugt/COMP18112/page3.html"
urlbase = "http://studentnet.cs.manchester.ac.uk/ugt/COMP18112/"

dom_struc = ''
links = list()

def process_link(link):
  if link[0] == '.':
    new_link = urlbase + link[2:]
    return new_link
  elif link[0] == '/':
    new_link = urlbase + link[1:]
    return new_link
  else:
    return link

class Node:

  def __init__(self, nr, father):
    self.nr = nr
    self.father = father
    self.attributes = []
    self.nodes = []
    self.text = ''
    self.tag = ''

def load_webpage(url):

  #initialization part
  data = urllib.urlopen(url)
  tokens = data.read().split()
  elements = list()
  global links
  links = list()
  global dom_struc
  dom_struc = ''

  #print tokens

  #-----------------------------------------------------------------
  #Split into elements

  for token in tokens:
    token = token.split('<')
    for split_token in token:
      split_token = split_token.split('>')
      for split2_token in split_token:
        elements.append(split2_token)

  print elements
  #task 1.2 -----------
  #Remove the html tags

  bold_start = '\033[1m\b'
  bold_end = '\033[0m\b'

  printable = True

  #-------------------------------------------------------
  #Functions for the browser

  check_html_errors = True

  #Deal with a link
  def add_link_to_list(node):
    for attribute in node.attributes:
      if "href" in attribute :
        link = attribute.split('"')[1]
        links.append(link)
    
  #process the link

  def check_close_tag_begin(index):
    if index == len(elements):
      return False
    if len(elements[index]) <= 1:
      return False
    return elements[index][0] == '/'

  def check_close_tag_is_correct(element):
    return dom[current_node].tag == element[1:]

  def get_dom_structure(index, indentation):
    node = dom[index]
    global dom_struc
    dom_struc = dom_struc + indentation + 'This is node: ' +  str(node.nr) + '\n'
    dom_struc = dom_struc + indentation + 'The father node is: ' + str(node.father) + '\n'
    dom_struc = dom_struc + indentation + str(node.tag) + '\n'
    dom_struc = dom_struc + indentation + str(node.attributes) + '\n'
    dom_struc = dom_struc + indentation + str(node.nodes) + '\n' 

    indentation = indentation + '  '
    #print

    for vec in node.nodes:
      get_dom_structure(vec, indentation)

  def get_html_structure(index, indentation):
    node = dom[index]
    global dom_struc
    dom_struc = dom_struc + indentation + str(node.tag)
    dom_struc = dom_struc + ' ' + node.text + '\n'

    indentation = indentation + '  '
    #print

    if(node.tag == 'a'):
      add_link_to_list(node)

    for vec in node.nodes:
      get_html_structure(vec, indentation)

  def interpret(node):
    
    if node.tag == 'title':
      print 'TITLE:', node.text,
    elif node.tag == 'h1':
      print '\nHEADING:', node.text,
    elif node.tag == 'p':
      print '\nPARAGRAPH:', node.text,
    elif node.tag == 'em':
      print bold_start, node.text, bold_end,
    elif node.tag == 'a':
      print node.text,

  def console_display(index):
    node = dom[index]
    #print node.tag + '/'
    interpret(node)

    for vec in node.nodes:
      console_display(vec)

  print '------------------------------------------'
  print bold_start, 'Beginning of the page', bold_end

  dom = []

  bignode = Node(0, -1)


  dom.append(bignode)
  nrnodes = 0
  newtag = True
  current_node = 0;
  index = -1
  ending = False

  for element in elements:
    #new node
    index = index + 1
    #Closing tag -> go up in the tree
    if(element == '' and check_close_tag_begin(index + 1)):
      #print 'a'
      ending = True
    #End of the closing tag
    elif(element == '' and ending):
      #print 'b'
      current_node = dom[current_node].father
      ending = False

    #new tag -> go down the tree
    elif(element == '' and newtag):
      #print 'c'
      newtag = not(newtag)
      
      #Increase the number of nodes
      nrnodes = nrnodes + 1;

      #Create node
      node = Node(nrnodes, current_node)

      #Add the new node to the DOM
      dom.append(node);

      #Do the lin between the current node and the new one
      dom[current_node].nodes.append(node.nr)

      #Update the cuurent node
      current_node = nrnodes

    #end of the new tag
    elif(element == '' and not(newtag)):
      #print 'd'
      newtag = not(newtag)

    #this is an attribute of the tag
    elif not(newtag) and not(ending) and dom[current_node].tag != '':
      #print 'e'
      dom[current_node].attributes.append(element)
    #this is the tag name
    elif not(newtag) and not(ending) and dom[current_node].tag == '':
      dom[current_node].tag = element
    #this is a piece of text inside the tag
    elif newtag and not(ending):
      #print 'f'
      dom[current_node].text = dom[current_node].text + ' ' + element
    #the closing tag
    elif newtag and ending:
      check_html_errors = False
      #Point to possible problems in html if the option is active
      if(not(check_close_tag_is_correct(element)) and check_html_errors):
        message = "Closing tag " + element + " is invalid. '"
        message = message + dom[current_node].tag + "' is expected"
        raise Exception(message)

  #Get the tree structure
  get_html_structure(1, '')

  #Friendly display in the console
  console_display(1)
  print

   
#-----------------------------------------------------------------
#GUI begin

class Browser(Frame):
  def __init__(self, parent):  
    Frame.__init__(self, parent, background="white")

    self.parent = parent
    self.initUI()
    self.go()

  def initUI(self):

    self.labels = []
    self.parent.title("Browser")
    self.pack(fill=BOTH, expand=1)
    self.placeWindow()

    self.columnconfigure(1, weight=1)
    self.columnconfigure(3, pad=7)
    self.rowconfigure(3, weight=1)
    self.rowconfigure(5, pad=7)
    
    self.area = Text(self)
    self.area.grid(row=1, column=0, columnspan=4, rowspan=4, 
              padx=5, sticky=E+W+S+N)
    
    self.abtn = Button(self, text="GO!", command=self.go)
    self.abtn.bind("<Return>", self.go)
    self.abtn.grid(row=0, column=3)

    self.entry = Entry(self)
    self.entry.grid(row=0, column=0, columnspan=3, padx=5, sticky=W+E)
    self.entry.insert(0, url1)

  def placeWindow(self):
    w = self.parent.winfo_screenwidth() - 200
    h = self.parent.winfo_screenheight() - 100

    self.parent.geometry('%dx%d+%d+%d' % (w, h, 10, 10))

  def click_label(self, event):
    link = event.widget["text"]
    new_link = process_link(link)
    self.entry.delete(0, END)
    self.entry.insert(0, new_link)
    self.go2(new_link)

  def add_links_gui(self):
    for label in self.labels:
      label.grid_forget()
    del self.labels
    self.labels = []
    
    row = 4
    index = -1
    global links

    self.link_header = Label(self, text='The first 10 links are: ').grid(row=5, 
                                                                    column = 0)
    for link in links:

      if index == 10:
        break

      index = index + 1
      self.labels.append(Label(self, text=link))
      self.labels[index].grid(row=index + 6, column=0)
      self.labels[index].bind('<Button-1>', self.click_label)

  def go(self):
    self.area.config(state=NORMAL)
    gui_url = self.entry.get()
    load_webpage(gui_url)
    self.area.delete(1.0, END)
    self.area.insert(INSERT, dom_struc)
    self.area.config(state=DISABLED)
    self.add_links_gui()

  def go2(self, url):
    self.area.config(state=NORMAL)
    load_webpage(url)
    self.area.delete(1.0, END)
    self.area.insert(INSERT, dom_struc)
    self.area.config(state=DISABLED)
    self.add_links_gui()


def main():
  master = Tk()
  master.geometry("1200x850+0+0")
  app = Browser(master)
  master.mainloop()

if __name__ == '__main__':
  main()

#-----------------------------------------------------------------
#GUI end
    
