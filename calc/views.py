from django.shortcuts import render
import bibtexparser
import seaborn as sns
import pandas as pd
import re
from collections import Counter
import matplotlib.pyplot as plt
from wordcloud import WordCloud, STOPWORDS
def month_string(string):
    m = {
        'jan': 'January',
        'feb': 'February',
        'mar': 'March',
        'apr': 'April',
        'may': 'May',
        'jun': 'June',
        'jul': 'July',
        'aug': 'August',
        'sep': 'September',
        'oct': 'October',
        'nov': 'November',
        'dec': 'December'
    }
    s = string.strip()[:3]
    s=s.lower()
    try:
        out = m[s]
        return out
    except:
        raise ValueError('Not a month')

# Create your views here.
def home(request):
    return render(request,'home.html')

def add(request):
	key=request.POST.get('keywd')
	Namelist=request.POST.getlist('File')
	parser = bibtexparser.bparser.BibTexParser(common_strings=True)	
	NumberOfFiles = len(Namelist)
	bib_database = [] 
	for i in range(NumberOfFiles):
		with open(Namelist[i]) as bibtex_file:
			bib_database.append(bibtexparser.loads(bibtex_file.read(),parser=parser))
	df = pd.DataFrame(bib_database[0].entries)
	l = len(df['month'])
	for i in range(l):
             if isinstance(df['month'][i],str):
                df['month'][i] = month_string(df['month'][i])
          
	if 'ENTRYTYPE' in df.keys():
		del df['ENTRYTYPE']
	if 'numpages' in df.keys():
		del df['numpages']
	if 'isbn' in df.keys():
		del df['isbn']	
	if 'issn' in df.keys():
		del df['issn']	
	if 'doi' in df.keys():
		del df['doi']	
	if 'volume' in df.keys():
		del df['volume']
	if 'articleno' in df.keys():
		del df['articleno']
	if 'issue_date' in df.keys():
		del df['issue_date']	
	df.to_csv('dataframe.csv', sep='|', index=False, encoding='utf-8')
		
	visulization_main('templates/images','dataframe.csv',key)
	return render(request,'add.html',{'img1':'/static/images/box_plot_month.png','img2':'/static/images/box_plot_year.png','img3':'/static/images/box_plot_publisher.png','img4':'/static/images/box_plot_keywords.png','img5':'/static/images/line_plot_keywords.png','img6':'/static/images/wordcloud.png'})


def bar_plot_year(dataframe,loc):
	sns_barplot = sns.countplot(x='year', data=dataframe)
	sns_barplot.set_xticklabels(sns_barplot.get_xticklabels(),rotation=90)
	sns_barplot.figure.savefig(str(loc)+"/box_plot_year.png", bbox_inches='tight',pad_inches = 0.0)
	plt.clf()

def bar_plot_month(dataframe,loc):
	dataframe['month'] = dataframe['month'].apply(lambda x: x if x != 'nan' else 'Dec')
	sns_barplot = sns.countplot(x='month', data=dataframe)
	sns_barplot.set_xticklabels(sns_barplot.get_xticklabels(),rotation=90)
	sns_barplot.figure.savefig(str(loc)+"/box_plot_month.png",bbox_inches='tight',pad_inches = 0.0)
	plt.clf()

"""def bar_plot_pages(dataframe,loc):
	dataframe['pages'] = dataframe['pages'].apply(lambda x:int(str(x).split("-")[1]) - int(str(x).split("-")[0]) if str(x).split("-")[0] != 'nan' else 0)
	# print(dataframe['pages'].value_counts(),dataframe['pages'].value_counts().index)
	sns_barplot = sns.countplot(x='pages', data=dataframe)
	sns_barplot.figure.savefig(str(loc)+"/box_plot_pages.png")
	plt.clf()"""

def bar_plot_publisher(dataframe,loc):
	dataframe['publisher'] = dataframe['publisher'].apply(lambda x: x if x != 'NaN' else 'NA')
	# print(dataframe['publisher'])
	sns_barplot = sns.countplot(x='publisher', data=dataframe)
	sns_barplot.set_xticklabels(sns_barplot.get_xticklabels(),rotation=90)
	sns_barplot.figure.savefig(str(loc)+"/box_plot_publisher.png",bbox_inches='tight',pad_inches = 0.0)
	plt.clf()

def bar_plot_keywords(dataframe,loc):
	unique_keywords = {}
	for i in range(0,len(dataframe)):
		# if df['keywords'][i] != 'NaN':
		keywds = re.split(',|;',str(dataframe['keywords'][i]))
		#keywds = str(dataframe['keywords'][i]).split(';')
		for kw in keywds:
			kw = kw.strip(' ')
			if kw.lower() in unique_keywords:
				unique_keywords[kw.lower()] +=1 
			else:
				unique_keywords[kw] = 1
	k_words = Counter(unique_keywords)
	high = k_words.most_common(10) 
	# print(unique_keywords)
	x = []
	y = []
	for words in high:
		x.append(words[0])
		y.append(words[1])
		# print(words[0]," ",words[1])
	cat=['keywords','values']
	df = pd.DataFrame({'keywords':x,'values':y})
	#print(df)
	sns_barplot = sns.barplot(x=df['keywords'], y=df['values'])
	# print(sns_barplot.get_xticklabels())
	sns_barplot.set_xticklabels(sns_barplot.get_xticklabels(),fontsize = 8,rotation=90)
	sns_barplot.figure.savefig(str(loc)+"/box_plot_keywords.png",bbox_inches='tight', pad_inches = 0.0)
	plt.clf()

def make_wordcloud(dataframe,loc):
	keywords = ''
	for i in range(0,len(dataframe)):
		# if df['keywords'][i] != 'NaN':
		keywds = re.split(',|;',str(dataframe['keywords'][i]))
		#keywds = str(dataframe['keywords'][i]).split(';')
		for kw in keywds:
			keywords += kw
	stopwords = set(STOPWORDS)
	wordcloud = WordCloud(width = 800, height = 800, 
                background_color ='white', 
                stopwords = stopwords, 
                min_font_size = 10).generate(keywords)
	fig = plt.figure() 
	plt.imshow(wordcloud) 
	plt.axis("off") 
	plt.tight_layout(pad = 0) 
	fig.savefig(str(loc)+"/wordcloud.png")
	plt.clf()

def make_keyword_lineplot(dataframe,loc,keywd):
	keywords_year_wise_count = {}
	for yr in dataframe.year.unique():
		keywords_year_wise_count[yr] = 0

	for i in range(0,len(dataframe)):
		# if df['keywords'][i] != 'NaN':
		keywds = re.split(',|;',str(dataframe['keywords'][i]))
		#keywds = str(dataframe['keywords'][i]).split(';')
		for kw in keywds:
			if kw.lower() == keywd:
				keywords_year_wise_count[dataframe['year'][i]]+=1
	# print(keywords_year_wise_count)
	# print(pd.DataFrame(keywords_year_wise_count.items(),columns=['year','count']))
	df = pd.DataFrame(keywords_year_wise_count.items(),columns=['year','count'])
	#print(df)
	sns_barplot = sns.lineplot(data=df,x="year", y="count").set_title(" Year wise appearence of keyword: "+str(keywd))
	#sns_barplot.set_xticklabels(sns_barplot.get_xticklabels(),fontsize = 8,rotation=90)
	sns_barplot.figure.savefig(str(loc)+"/line_plot_keywords.png",bbox_inches='tight',pad_inches = 0.0)
	plt.clf()
	# print(pd.DataFrame.from_dict(keywords_year_wise_count,orient='index',columns=['year','count']))



# def line_plot(x,y,dataframe,hue_val):
# 	sns_lineplot = sns.relplot(x=x, y=y, hue=hue_val, kind="line", data=dataframe)
# 	return sns_lineplot

def visulization_main(loc,dataframe_loc,keyword):
	df = pd.read_csv(dataframe_loc,sep="|")
	bar_plot_year(df,loc)
	bar_plot_month(df,loc)
	#bar_plot_pages(df,loc)
	bar_plot_publisher(df,loc)
	bar_plot_keywords(df,loc)
	make_wordcloud(df,loc)
	make_keyword_lineplot(df,loc,keyword)
