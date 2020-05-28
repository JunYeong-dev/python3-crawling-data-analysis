import urllib.request
from bs4 import BeautifulSoup
import pandas as pd
import matplotlib.pyplot as plt

# 네이버 영화 리뷰 크롤링
# 리뷰 정보 클래스
class Review:

    def __init__(self, comment, date, star, good, bad):
        self.comment = comment
        self.date = date
        self.star = star
        self.good = good
        self.bad = bad

    def show(self):
        print("내용: " + self.comment +
              "\n날짜: " + self.date +
              "\n별점: " + self.star +
              "\n좋아요: " + self.good +
              "\n싫어요: " + self.bad)

    # 리뷰 정보 크롤링 함수
    def crawl(url):
        soup = BeautifulSoup(urllib.request.urlopen(url).read(), "html.parser")
        # 리뷰 정보를 담을 리스트
        review_list = []
        title = soup.find("h3", class_="h_movie").find("a").text
        div = soup.find("div", class_="score_result")
        data_list = div.select("ul > li")

        for review in data_list:
            star = review.find("div", class_="star_score").text.strip()
            reply = review.find("div", class_="score_reple")
            comment = reply.find("p").text
            date = reply.select("dt > em")[1].text.strip()
            button = review.find("div", class_="btn_area")
            good = button.find("a", class_="_sympathyButton").find("strong").text
            bad = button.find("a", class_="_notSympathyButton").find("strong").text
            review_list.append(Review(comment, date, star, good, bad))

        return title, review_list
    
    # 데이터 프레임화
    def get_summary(review_list):
        star_list = []
        good_list = []
        bad_list = []

        for review in review_list:
            star_list.append(int(review.star))
            good_list.append(int(review.good))
            bad_list.append(int(review.bad))

        star_series = pd.Series(star_list)
        good_series = pd.Series(good_list)
        bad_series = pd.Series(bad_list)

        summary = pd.DataFrame({
            'Star': star_series,
            'Good': good_series,
            'Bad': bad_series,
            # Score : 댓글에 대한 평가 중 좋아요의 비율
            'Score': good_series / (good_series + bad_series)
        })

        return summary

    def movie_compare(review_lists):
        count = 1
        x = []
        y = []
        for movie, review_list in review_lists:
            x.append(count)
            summary = Review.get_summary(review_list)
            # 댓글의 좋아요 비율이 90% 보다 큰 것만
            summary = summary[summary['Score'] > 0.9]
            y.append(summary['Star'].mean())
            count += 1
        plt.bar(x, y)
        plt.title('Movie Star')
        plt.xlabel('Movie Number')
        plt.ylabel('Movie Average')
        plt.show()

title, review_list = Review.crawl("https://movie.naver.com/movie/bi/mi/basic.nhn?code=30688")
print("제목: " + title)
for review in review_list:
    review.show()

movie_code_list = [30688, 31794, 39440]
review_lists = []

for i in movie_code_list:
    title, review_list = Review.crawl("https://movie.naver.com/movie/bi/mi/basic.nhn?code=" + str(i))
    summary = Review.get_summary(review_list)
    print("[ %s ]" % (title))
    print(summary)
    review_lists.append((title, review_list))

Review.movie_compare(review_lists)