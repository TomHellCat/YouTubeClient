import sys
import re
import time
from datetime import datetime, timedelta
import requests
from bs4 import BeautifulSoup
from textblob import TextBlob
import matplotlib.pyplot as plt 

non_bmp_map = dict.fromkeys(range(0x10000, sys.maxunicode + 1), 0xfffd)

class VideoInfo(object):

    def __init__(self,url,title):
        self.url = url
        self.title = title
        self.total_views = 0
        self.sentiment = 0

    def __del__(self):
        print("Deleting...")

    def remove_special_characters(self,text):
        text = ''.join(e for e in text if e.isalnum())
        return text
        
    def get_video(self):
        markup = requests.get(self.url).text
        soup = BeautifulSoup(markup,'html.parser')
        self.likes = soup.findAll('button',{"title":"I like this"})
        self.dislikes = soup.findAll('button',{"title":"I dislike this"})
        self.views = soup.findAll('div',{"class":"watch-view-count"})
        self.pub = soup.findAll('strong', {"class":"watch-time-text"})

    def get_sentiment(self):
        text = self.title
        print("text: ", text.encode("utf-8"))
        text =  ' '.join(re.sub("(@[A-Za-z0-9]+)|([^0-9A-Za-z \t]) |(\w+:\/\/\S+)", " ", text).split())
        analysis = TextBlob(text)
        if(analysis.sentiment.polarity >= 0):
            return 1
        else:
            return 0

    def retry(self,title,p):
        r = 0
        while((len(self.likes) == 0 or len(self.dislikes) == 0 or len(self.views) == 0) and r < 3 ):
            print("No reponse from the server retrying in 3 seconds")
            r += 1
            time.sleep(3)
            self.get_video
        if(r >= 3):
            print("No ",p," info available for " ,title)
            

    def get_likes(self):
        try:
            if(len(self.likes) > 0):
                like_span = self.likes[0].findAll('span')
                if(len(like_span) > 0):
                    likes = like_span[0].contents[0]
                    likes = self.remove_special_characters(likes)
                    return int(likes)
                else:
                    return None
            else:
                return None
        except IndexError:
            return None
    
    def get_dislikes(self):
        
        if(len(self.dislikes) > 0):
            dislike_span = self.dislikes[0].findAll('span')
            if(len(dislike_span) > 0):
                dislikes = dislike_span[0].contents[0]
                dislikes = self.remove_special_characters(dislikes)
                return int(dislikes)
            else:
                return None
        else:
            return None
    
    def get_views(self):
        try:
            if(len(self.views) > 0):
                if(len(self.views[0].contents[0]) > 0):
                    v = re.sub(r"[^0-9]+",'',self.views[0].contents[0])
                    self.total_views += int(v)
                    return int(v)
                else:
                    return None
        except IndexError:
            return None
            
    
    def scrape_date(self):
        if(len(self.pub) > 0):
            print("Time: ",self.pub[0].contents)
            d = self.get_date(self.pub[0].contents)
            print("Date: ",d)
            return d

        else:
            print("Info not available")
            return None
       
    def get_date(self,l):
        date = ''
        format = "%d %b %Y"
        
        if(l[0][0] == 'P' and l[0][1] == 'r'):     #if the published date is of the format: Premiered x minutes/hours/days ago    
            print(" if p and r: ", l[0])
            digit = ''
            if(l[0][10].isdigit()):
                now = datetime.now()
                print("now: ", now)
                digit = l[0][10]
                if(l[0][11].isdigit()):
                    digit += l[0][11]
                    print("digit", digit)
                if(l[0][10 + len(digit) + 1] == 'h'):
                    now = now - timedelta(hours=int(digit))
                    print("hours")
                elif(l[0][10 + len(digit) + 1] == 'm' and l[0][10 + len(digit) + 2] == 'i'):
                    now = now - timedelta(minutes=int(digit))
                    print("minutes")
                elif(l[0][10 + len(digit) + 1] == 'd'):
                    now = now - timedelta(days=int(digit))
                    print("days")
                elif(l[0][10 + len(digit) + 1] == 'm'):
                    now = now - timedelta(days=int(digit) * 30)
                    print("months")
                elif(l[0][10 + len(digit) + 1] == 'y'):
                    now = now - timedelta(days=int(digit) * 30 * 12)
                    print("years")
                return n
            
            elif(l[0][13].isdigit()):        #if the published date is of the format: Premiered on dd m yyyy
                for i in range(13,len(l[0])):
                    digit += l[0][i]
                return datetime.strptime(digit, format)
            
        elif(l[0][0] == 'P'):                 #if the published date is of the format: Published on dd m yyyy
            print("if P: ",l[0])
            for i in range(13,len(l[0])):
                date = date + l[0][i]
            return datetime.strptime(date, format)
                
        elif(l[0][0] == 'S' and l[0][1] == 't'):    
            if(l[0][18] == 'o' and l[0][17] == " "):                    #if the published date is of the format: Started streaming on dd m yyyy
                for i in range(21,len(l[0])):
                    date = date + l[0][i]
                return datetime.strptime(date, format)

            elif(l[0][2] == 'r' and l[0][14] == 'o'):
                j = 17
                for i in range(j, len(l[0])):
                    date = date + l[0][i]
                return datetime.strptime(date, format)
                
            elif(l[0][2] == 'r'):
                j = 14
                digit = ''
                print("l[0][j]: ", l[0][j])
                while(l[0][j] != " "):
                    digit += l[0][j]
                    j += 1
                print("digit: ", digit)
                j += 1
                if(l[0][j] == 'h'):
                    print("l[0][j]: ", l[0][j])
                    now = datetime.now()
                    now = now - timedelta(hours=int(digit))
                    return now
                elif(l[0][j] == 's'):
                    print("l[0][j]: ", l[0][j])
                    now = datetime.now()
                    return now
                    
                elif(l[0][j] == 'm'):
                    print("l[0][j]: ", l[0][j])
                    now = datetime.now()
                    now = now - timedelta(minutes=int(digit))
                    return now
                elif(l[0][j] == 'm' and 'o'):
                    print("l[0][j]: ", l[0][j])
                    now = datetime.now()
                    now = now - timedelta(days=30*int(digit))
                    return now
                elif(l[0][j] == 'd'):
                    print("l[0][j]: ", l[0][j])
                    now = datetime.now()
                    now = now - timedelta(days=int(digit))
                    return now
            
            else:
                j = 18
                digit = ''
                while(l[0][j] != " "):
                    digit += l[0][j]
                    j += 1
                print("digit: ", digit)
                j += 1
                if(l[0][j] == 'h'):
                    print("l[0][j]: ", l[0][j])
                    now = datetime.now()
                    now = now - timedelta(hours=int(digit))
                    return now
                    
                elif(l[0][j] == 'm'):
                    print("l[0][j]: ", l[0][j])
                    now = datetime.now()
                    now = now - timedelta(minutes=int(digit))
                    return now

                elif(l[0][j] == 's'):
                    print("l[0][j]: ", l[0][j])
                    now = datetime.now()
                    now = now - timedelta(seconds=int(digit))
                    return now

                elif(l[0][j] == 'd'):
                    print("l[0][j]: ", l[0][j])
                    now = datetime.now()
                    now = now - timedelta(days=int(digit))
                    return now
            
        else:
            digit = ''
            print("else: ", l[0])
            
            if(l[0][14].isdigit()):
                now = datetime.now()
                print("now: ", now)
                digit = l[0][14]
                if(l[0][15].isdigit()):
                    digit += l[0][15]
                    print("digit", digit)
                if(l[0][14 + len(digit) + 1] == 'h'):
                    now = now + timedelta(hours=int(digit))
                    print("hours")
                elif(l[0][14 + len(digit) + 1] == 'm' and l[0][14 + len(digit) + 2] == 'i'):
                    now = now + timedelta(minutes=int(digit))
                    print("minutes")
                elif(l[0][14 + len(digit) + 1] == 'd'):
                    now = now + timedelta(days=int(digit))
                    print("days")
                elif(l[0][14 + len(digit) + 1] == 'm'):
                    now = now + timedelta(days=int(digit) * 30)
                    print("months")
                elif(l[0][14 + len(digit) + 1] == 'y'):
                    now = now + timedelta(years=int(digit) * 30)
                    print("years")
                print(type(now))
                
                return now
            else:
                        
                for i in range(18,len(l[0])):
                    date = date + l[0][i]
        return date

    def monthlist_fast(self,start,end):
        #start, end = [datetime.strptime(_, "%d %b %Y") for _ in dates]
        total_months = lambda dt: dt.month + 12 * dt.year
        mlist = []
        for tot_m in range(total_months(start)-1, total_months(end)):
            y, m = divmod(tot_m, 12)
            mlist.append(datetime(y, m+1, 1).strftime("%b %Y"))
        return mlist    
 

class YoutubeClient(object):
    
    def __init__(self,keyword):
        self.search_term = keyword
        search_term = re.sub(r"[^a-zA-Z0-9]+", ' ', keyword)
        search_term = search_term.replace(" ","+")
        self.url = 'https://www.youtube.com/results?search_query=' + search_term

    def remojies(self,text):          #remove emojies

      EMOJI_PATTERN = re.compile(
        "(["
        "\U0001F1E0-\U0001F1FF"  # flags (iOS)
        "\U0001F300-\U0001F5FF"  # symbols & pictographs
        "\U0001F600-\U0001F64F"  # emoticons
        "\U0001F680-\U0001F6FF"  # transport & map symbols
        "\U0001F700-\U0001F77F"  # alchemical symbols
        "\U0001F780-\U0001F7FF"  # Geometric Shapes Extended
        "\U0001F800-\U0001F8FF"  # Supplemental Arrows-C
        "\U0001F900-\U0001F9FF"  # Supplemental Symbols and Pictographs
        "\U0001FA00-\U0001FA6F"  # Chess Symbols
        "\U0001FA70-\U0001FAFF"  # Symbols and Pictographs Extended-A
        "\U00002702-\U000027B0"  # Dingbats
        "\U000024C2-\U0001F251" 
        "])"
      )
      text = re.sub(EMOJI_PATTERN, r' \1 ', text)
      return text

    def get_search_results(self):
        try:
            markup = requests.get(self.url).text
        except requests.exceptions.Timeout as e:
            print("The server didn't respond on time")
            raise SystemExit(e)
        except requests.exceptions.TooManyRedirects as e:
            print("We are getting too many redirects please try someother keywords")
            raise SystemExit(e)
        except requests.exceptions.RequestException as e:
            print("We can't seem to reach our servers. Are you sure you are connected to the internet?")
            raise SystemExit(e)
            
        soup = BeautifulSoup(markup,'html.parser')
        links = soup.findAll('a',{"class":"yt-uix-tile-link yt-ui-ellipsis yt-ui-ellipsis-2 yt-uix-sessionlink spf-link"})
        return links

    def retry(self,links):
        while(len(links) == 0):
            print("No response from the server retrying within 3 seconds")
            time.sleep(3)
            links = self.get_search_results()
        else:
            return links
    
    def get_urls_and_titles(self):
        links = self.retry(self.get_search_results())
        url = 'https://www.youtube.com'
        url_list = []
        title_list = []
        channel =''
        for link in links:
            l = link.get('href')
            for i in range(8):
                channel += l[i]
            if(channel != '/channel'):
                url_list.append(url+l)
                text = link.contents
                title_list.append(self.remojies(text[0]))
            channel = ''
        return url_list,title_list

    def create_video_info_objects(self):
        self.video_info_list = []
        url_list, title_list = self.get_urls_and_titles()
        for i in range(len(url_list)):
            v = VideoInfo(url_list[i],title_list[i])
            v.get_video()
            if(len(v.likes) == 0 or len(v.dislikes) == 0 or len(v.views) == 0):
                print("Not including: ",v.title.encode("utf-8"))
                del v
            else:
                self.video_info_list.append(v)
        print(len(self.video_info_list), " videos analysed")
        
            

    def get_months(self):
        self.months = []
        for i in range(len(self.video_info_list)):
            if(isinstance(self.video_info_list[i].scrape_date(), datetime)):
                print(self.video_info_list[i].title.encode("utf-8") ,": ",self.video_info_list[i].url)
                self.months.append(self.video_info_list[i].scrape_date())
        self.months = sorted(self.months)
        return self.months

    def get_total_fav_unfav(self):
        fav = 0
        unfav = 0
        for i in self.video_info_list:
            print(i.get_sentiment())
            if(i.get_sentiment()):
                fav += 1
                i.sentiment = 1
            else:
                unfav += 1
                i.sentiment = 0
        return fav,unfav

    def total_likes_fav_unfav(self):
        fav = 0
        unfav = 0
        for i in self.video_info_list:
            print(i.sentiment)
            if(i.sentiment == 1):
                print(i.get_likes())
                if(i.get_likes() != None):
                    fav += i.get_likes()
            else:
                if(i.get_likes() != None):
                    unfav += i.get_likes()
        return fav,unfav

    def total_dislikes_fav_unfav(self):
        fav = 0
        unfav = 0
        for i in self.video_info_list:
            print(i.sentiment)
            if(i.sentiment == 1):
                print(i.get_dislikes())
                if(i.get_dislikes() != None):
                    fav += i.get_dislikes()
            else:
                if(i.get_dislikes() != None):
                    unfav += i.get_dislikes()
        return fav,unfav

    def fav_unfav_monthlist(self,month):
        fav = []
        unfav = []
        for i in range(len(month)):
            if(self.video_info_list[i].sentiment == 1):
                fav.append(month[i])
            else:
                unfav.append(month[i])
        return fav,unfav


    def get_total_views(self):
        views = 0
        self.views_list = []
        for i in self.video_info_list:
            self.views_list.append(i.get_views())
            if(i.get_views() != None):
                views += i.get_views()
        print(self.views_list)
        return views



    def monthlist_fast(self,start,end):
        #start, end = [datetime.strptime(_, "%d %b %Y") for _ in dates]
        total_months = lambda dt: dt.month + 12 * dt.year
        mlist = []
        for tot_m in range(total_months(start)-1, total_months(end)):
            y, m = divmod(tot_m, 12)
            mlist.append(datetime(y, m+1, 1).strftime("%b %Y"))

        return mlist

    def get_y_axis(self,mlist,months):
        y_axis = [0] * len(mlist)
        for i in months:
            for j in range(len(mlist)):
                if(i.strftime("%b %Y") == mlist[j]):
                    y_axis[j] += 1
        return y_axis

    def plot_graph(self,x,y):
        plt.plot(x, y) 
        plt.xlabel('months') 
        plt.ylabel('Videos Published') 
          

        plt.title('Timeline of Videos Published') 

        plt.show()

    def plot2(self,x,y1,y2):
        plt.plot(x,y1,"g")
        plt.plot(x,y2,"r")
        plt.xlabel('Months') 
        plt.ylabel('Videos Published') 
        plt.title('Timeline of Videos Published') 
        plt.show()


            
                                   
            
    
def main():
    yt = YoutubeClient("Tesla Model S")
    yt.create_video_info_objects()
    format = "%d %b %Y"
    

    
    months = yt.get_months()
    print(len(months))
    m = yt.monthlist_fast(months[0],months[len(months)-1])
    for i in months:
        print(i.strftime(format))
    print(m)
    y = yt.get_y_axis(m,months)
    print(y)
    fav,unfav = yt.get_total_fav_unfav()
    print("fav: ",fav, " unfav: ",unfav)
    
    print("views: ", yt.get_total_views())
    lfav,lunfav = yt.total_likes_fav_unfav()

    print("likes for fav: ",lfav," likes for unfav: ", lunfav)

    dfav, dunfav = yt.total_dislikes_fav_unfav()

    print("dislikes for fav: ",dfav," dislikes for unfav: ", dunfav)
    t_fav = lfav + dunfav
    t_unfav = lunfav + dfav
    print("t_fav: ", t_fav, " t_unfav: ", t_unfav)

    m_fav,m_unfav = yt.fav_unfav_monthlist(months)
    print("m_fav: ")
    for i in m_fav:
        print(i.strftime(format))
    print("m_unfav: ")
    for i in m_unfav:
        print(i.strftime(format))

    y_fav = yt.get_y_axis(m,m_fav)
    print("y_fav: ",y_fav)
    y_unfav = yt.get_y_axis(m,m_unfav)
    print("y_unfav: ", y_unfav)

    new_m = []
    for i in m:
        s = ''
        j = 0
        while(i[j] != " "):
            s += i[j]
            j += 1
        s += "\n"
        j += 1
        for k in range(j,len(i)):
            s += i[k]
        new_m.append(s)

    print(new_m)

    yt.plot_graph(m,y)
    yt.plot2(new_m,y_fav,y_unfav)


    

if __name__ == "__main__":
    main()
