from bs4 import BeautifulSoup
import requests
import json
import os
import sys
import time
import re

baseurl = "https://askubuntu.com"
headers = requests.utils.default_headers()
headers.update({
    'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:103.0) Gecko/20100101 Firefox/103.0',
})

sample_user_link = 'https://askubuntu.com/users/346507/kerner1000'

def single_user_crawler(site_link):
    
    temp = site_link.split("/")
    user_dict = {
        "link": site_link,
        "id": int(temp[-2]),
    }

    try:
        response = requests.get(site_link, headers=headers)
        if(response.status_code != 200):
            raise Exception("Unexpected Response")

        html = response.text
        soup = BeautifulSoup(html, 'html.parser')

        """
        Username
        """
        username = ""
        try:
            username_soup = soup.find(class_ = "fs-headline2")
            username = username_soup.get_text().strip()
            # print(username.get_text().strip())
        except:
            pass
        

        """
        About, Location, joined_on
        """ 
        about,location,joined_on  = None, None, None
        try:
            info_soup = soup.find_all(class_ = "s-anchors")
            joined_on = info_soup[0].find("span")["title"]
            location = soup.find("svg", class_ = "iconLocation").find_parent().find_parent().get_text().strip()
        except:
            pass

        try:
            about_soup = soup.find(class_ = "js-about-me-content")
            about = about_soup.get_text().strip()
            # print(about)
        except:
            pass

        """
        Statistics:
            Reputation, Reach, Answers , Questions, 
        """

        reputation, reach, questions, answers = None, None, None, None
        try:
            user_stats_table = soup.find(id = 'stats')
            stats = user_stats_table.find_all(class_ = "fs-body3")
        
            # Reputation
            reputation = stats[0].get_text().strip()
            reputation = int(reputation.replace(",", ""))
            # print(reputation)

            # Reach
            reach = stats[1].get_text().strip()
            # print(reach)

            # Answers
            answers = int(stats[2].get_text().strip().replace(",", ""))
            # print(answers)

            # Questions
            questions = int(stats[3].get_text().strip().replace(",", ""))
            # print(questions)
        
        except:
            pass

        """
        Top Tags
        """
        top_tags = []
        try:
            top_tags_table = soup.find(id = "top-tags")
            top_tags_soup = top_tags_table.find_all(class_ = "s-tag")  
            top_tags = [tag.get_text().strip() for tag in top_tags_soup]
        except:
            pass


        """
        Communities
        """
        communities = []
        try:
            communities_soup = soup.find(id = "stats").find_parent().find("ul")
            all_communities = communities_soup.find_all("li")
            for c in all_communities:
                # print(c)
                items = c.find_all("div")[:4]
                try:
                    community_dict = {
                        "community": items[1].get_text().strip(),
                        "profile_link": c.find("a")["href"],
                        "reputation": items[3].get_text().strip()
                    }

                    communities.append(community_dict)
                except:
                    pass
        except:
            pass


        """
        Top Badges and count of badges
        """
        badges = {}
        try:
            "Gold"
            gold_badges_soup = soup.find("svg", class_ = "fc-gold").find_parent().find_parent().find_parent()
            # print(gold_badge.text)
            top_badges_soup = gold_badges_soup.find_all("a")

            badges["gold"] = {
                "count" : gold_badges_soup.find("div", class_ = "fs-title").get_text().strip(),
                "top_badges" : [b.get_text().strip() for b in top_badges_soup],
            }

            "Silver"
            silver_badges_soup = soup.find("svg", class_ = "fc-silver").find_parent().find_parent().find_parent()
            top_badges_soup = silver_badges_soup.find_all("a")

            badges["silver"] = {
                "count" : silver_badges_soup.find("div", class_ = "fs-title").get_text().strip(),
                "top_badges" : [b.get_text().strip() for b in top_badges_soup],
            }

            "Bronze"
            bronze_badges_soup = soup.find("svg", class_ = "fc-bronze").find_parent().find_parent().find_parent()
            top_badges_soup = bronze_badges_soup.find_all("a")

            badges["bronze"] = {
                "count" : bronze_badges_soup.find("div", class_ = "fs-title").get_text().strip(),
                "top_badges" : [b.get_text().strip() for b in top_badges_soup],
            }
            
        except:
            pass
        
        user_dict.update({
            "username" : username,
            "location" : location,
            "joined_on" : joined_on,
            "about": about,
            "reputation" : reputation,
            "reach" : reach,
            "answers" : answers,
            "questions" : questions,
            "communities": communities,
            "badges": badges,
            "top_tags" : top_tags,
        })

    except Exception as e:
        print(e)
        with open("logs/scrape_user_error_log.txt","a") as f:
            f.write(f"{site_link}\n")

        time.sleep(180)

    # print(json.dumps(user_dict, indent=4))
    return user_dict

def pagewise_user_crawler(page):

    query = f"/users?page={page}"
    query_url = baseurl + query

    page_user_list = []

    print(f"Querying Page {page}: ==> " + query_url)
    try:
        response = requests.get(query_url, headers=headers)
        if(response.status_code != 200):
            raise Exception("Unexpected Response")

        html = response.text
        soup = BeautifulSoup(html, 'html.parser')
        users = soup.find_all(class_="user-info")

        # print(len(users))
        for user in users:
            user_site_link = user.find("a", href = True)["href"]
            absolute_user_link = baseurl + user_site_link
            user_dict = single_user_crawler(absolute_user_link)
            page_user_list.append(user_dict)
            # print(user_site_link["href"])

    except Exception as e:
        print(e)
        with open("logs/page_scrape_error_log.txt","a") as f:
            f.write(f"Description: {e}\n")
        
        time.sleep(180)

    print(f"Finished page {page}\n")
    return page_user_list

def main():

    try:
        page_start = int(sys.argv[1])
        page_end = int(sys.argv[2])
    except:
        page_start = int(input("Enter Start Page: "))
        page_end = int(input("Enter End page(excludes the last page): "))

    current_batch_users = []
    for page in range(page_start, page_end):
        current_page_users = pagewise_user_crawler(page)
        current_batch_users.extend(current_page_users)
        time.sleep(1)

    with open(f"users_data/users_page{page_start}-page{page_end-1}.json", "w", encoding="utf-8") as f:
        json.dump(current_batch_users, f, indent=4)


if __name__ == "__main__":
    os.makedirs('users_data', exist_ok=True)
    os.makedirs('logs', exist_ok=True)

    # single_user_crawler(sample_user_link)
    # pagewise_user_crawler(1)
    main()
