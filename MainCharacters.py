#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Mon Jun  3 22:09:19 2019

@author: ajay
"""

import re
import nltk
parseData = open('/Users/ajay/Desktop/wizard.txt','r').read()
characters= re.findall(r'(?<=[a-z] )[A-Z][a-z]+', parseData)
names=set(characters)
#vs parsing data itself
new_list=[]
for sent in nltk.sent_tokenize(parseData):
    for chunk in nltk.ne_chunk(nltk.pos_tag(nltk.word_tokenize(sent))):
        if hasattr(chunk, 'label'):
            if(chunk.label()=='PERSON'):
                new_list.append(chunk[0][0])
funnel= names.intersection(set(new_list))
print "FUNNEL ATTEMPT ONE"
print funnel
wordList=""
funnel_2=[]
for word in funnel:
    wordList=wordList+word+", "
final_funnel=nltk.word_tokenize(wordList)
print "WORD PART OF SPEECHES"
print nltk.pos_tag(final_funnel)
for chunk in nltk.ne_chunk(nltk.pos_tag(nltk.word_tokenize(wordList))):
    if hasattr(chunk, 'label'):
        #if(chunk.label()=='PERSON'): #excludes words like oz which are 'GPE', should be something like exclude common words and adverbs
        funnel_2.append(chunk[0][0])
        print(chunk.label(), ' '.join(c[0] for c in chunk))
print " TEMPORARY 2ND FUNNEL"
print funnel_2  
