import urllib2
from urlparse import urlparse

new_url_file = "C:\\Users\\jatkinson\\Desktop\\holidayled_urls.csv";
articles_link = "http://holidayleds.com/articles?page=";

class HttpDownloader:
	def __init__(self, url):
		self.url = url;

	def download(self):
		response = urllib2.urlopen(self.url);
		return response.read();

class FindString:
	def __init__(self, pattern, content, delimiter, offset=0):
		self.pattern = pattern;
		self.content = content;
		self.delimiter = delimiter;
		self.offset = offset;

	def results(self, start_index=-1, previous=""):
		pos = self.content.find(self.pattern, start_index + 1);
		if pos == -1:
			return [];
		else:
			pos += self.offset;
		link = self.content[pos:].partition(self.delimiter)[0];
		return [link] + self.results(pos, link)

def downloadArticles(url):
	for page in range(0, 15):
		downloader = HttpDownloader(url + str(page));
		article_link_page = downloader.download();
		get_urls = FindString("<span class=\"field-content\"><a href=\"/articles/",
			                  article_link_page, "\">", 38)
		urls = list(set(get_urls.results()));
		for link in urls:
			page = open("articles\\" + link[9:] + ".aspx", 'w');
			web_browser = HttpDownloader("http://holidayleds.com/" + link);
			try:
				page_data = web_browser.download();
			except:
				pass;
			find_string = FindString("<div id=\"content-inner\" class=\"clear\">",
				                     page_data, "</div><!-- /content -->", 0);
			content = ''.join(find_string.results());
			content = changeurls(content)
			pos = content.find("<div class=\"links\">");
			content = content.replace(content[pos:], "");
			content += "</div>" * 3;
			page.write(content);
			page.close()

def changeurls(content):
	get_urls = FindString("<a href=\"http://www.holidayleds.com/", content, "\">", 16)
	old_urls = get_urls.results()
	new_urls = open(new_url_file).read().splitlines()

	ignore_list = ["christmas-light-applications", "christmas-light-shapes",
	               "christmas-tree-lights", "battery-christmas-lights",
	               "commercial-wholesale", "christmas-light-colors"]
	for url in old_urls:
		split_url = url.split("/");
		split_url = [link.replace("target=\"_blank\"", "") for link in split_url]
		split_url = [link.replace("_", "-") for link in split_url]
		if split_url[1] == "search":
			continue

		if split_url[1] == "articles":
			split_url[0] = "blog.holidayleds.com"
			content = content.replace(url, '/'.join(split_url))
			continue

		matching = [s for s in new_urls if split_url[-1] in s]
		if len(matching) == 1 and split_url not in ignore_list:
			content = content.replace(split_url[-1], matching[0].split('/')[-1])
		elif (split_url[-1] != "" and split_url[-1][-5:] != ".aspx"):
			split_url[-1] += ".aspx"
			content = content.replace(url, '/'.join(split_url))
	return content;

if __name__ == "__main__":
	downloadArticles(articles_link);
