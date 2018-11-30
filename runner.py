import dataclasses
import os
import requests
import youtube_dl

from bs4 import BeautifulSoup


@dataclasses.dataclass()
class CrawlingURLForSongs:
    url: str

    def __post_init__(self):
        print("Crawling through the URL -> %s for songs now ..." % self.url)
        self.list_of_songs = []

    def __scrape_for_songs(self):
        r = requests.get(self.url)
        songs_div_elem = BeautifulSoup(r.text, 'html.parser').findAll("div", {"class": "chart-item-info"})
        for elem in songs_div_elem:
            song = ""
            for s in elem.find_all('a'):
                song += " " + s.string
            self.list_of_songs.append(song)
        print("\n".join(self.list_of_songs))
        return self.list_of_songs

    def run(self):
        self.__scrape_for_songs()
        return self.list_of_songs


@dataclasses.dataclass()
class DownloadTheSongFromYT:
    song_name: str
    YOUTUBE_URL = "https://www.youtube.com"

    def __post_init__(self):
        print("Searching for the song %s from YouTube.." % self.song_name)
        self.__find_the_link()
        self.__let_the_download_begin()

    def __find_the_link(self):
        r = requests.get(self.YOUTUBE_URL + "/results?search_query=%s" % self.song_name)
        songs_div_elem = BeautifulSoup(r.text, 'html.parser').select('a[href*="/watch?v"]')
        self.hash_code = songs_div_elem[0]['href']

    def __let_the_download_begin(self):
        ydl_opts = {
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '320',
            }],

        }
        self.song_url = self.YOUTUBE_URL + self.hash_code
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            print("The song %s is being downloaded from URL -> %s" % (self.song_name, self.song_url))
            ydl.download([self.song_url])


@dataclasses.dataclass()
class Manager:
    URLS = ["https://www.at40.com/charts/hot-ac-243/latest/", "https://www.at40.com/charts/top-40-238/latest/"]
    dest_dir_path: str = "/Users/Shyam/Downloads/Songs/"
    src_dir_path: str = os.getcwd()

    def cleanup_before(self):
        pass

    def cleanup_after(self):
        self.create_dir()
        self.move_songs_to_dir()

    def move_songs_to_dir(self):
        for file in os.listdir(self.src_dir_path):
            if file.endswith(".mp3"):
                os.rename(src=self.src_dir_path + "/" + file, dst=self.dest_dir_path + "/" + file)

    def create_dir(self):
        if not os.path.exists(self.dest_dir_path):
            os.mkdir(self.dest_dir_path)
            print("Directory ", self.dest_dir_path, " Created.")
        else:
            print("Directory ", self.dest_dir_path, " already exists..")

    def downloading(self):
        for i in self.URLS:
            songs_queue = CrawlingURLForSongs(i).run()
            for song in songs_queue:
                DownloadTheSongFromYT(song)

    def run(self):
        self.cleanup_before()
        self.downloading()
        self.cleanup_after()


if __name__ == "__main__":
    Manager().run()

