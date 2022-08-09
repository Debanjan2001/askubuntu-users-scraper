from bs4 import BeautifulSoup
import requests
import json
import os

baseurl = "https://askubuntu.com"
headers = requests.utils.default_headers()
headers.update({
    'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:103.0) Gecko/20100101 Firefox/103.0',
})

sample_user_link = 'https://askubuntu.com/users/231142/terrance'

def single_user_crawler(site_link):
    
    temp = site_link.split("/")
    user_dict = {
        "link": site_link,
        "id": int(temp[-2]),
    }

    try:
        response = requests.get(site_link, headers=headers)
        html = response.text
        soup = BeautifulSoup(html, 'html.parser')

        """
        Username
        """
        username = soup.find(class_ = "fs-headline2")
        
        # print(username.get_text().strip())
        user_dict["name"] = username.get_text().strip()

        """
        Statistics:
            Reputation, Reach, Answers , Questions, 
        """
        user_stats_table = soup.find(id = 'stats')
        stats = user_stats_table.find_all(class_ = "fs-body3")
        
        # Reputation
        reputation = stats[0].get_text().strip()
        reputation = int(reputation.replace(",", ""))
        # print(reputation)
        user_dict["reputation"] = reputation

        # Reach
        reach = stats[1].get_text().strip()
        # print(reach)
        user_dict["reach"] = reach

        # Answers
        answers = int(stats[2].get_text().strip().replace(",", ""))
        # print(answers)
        user_dict["answers"] = answers

         # Questions
        questions = int(stats[3].get_text().strip().replace(",", ""))
        # print(questions)
        user_dict["questions"] = questions

        """
        Top Tags
        """
        top_tags_table = soup.find(id = "top-tags")
        top_tags_soup = top_tags_table.find_all(class_ = "s-tag")  
        top_tags = [tag.get_text().strip() for tag in top_tags_soup]
        user_dict["top_tags"] = top_tags 

    except Exception as e:
        print(e)
        with open("log.txt","a") as f:
            f.write(f"Site: {site_link}\n")
            f.write(f"Description: {e}\n")

    # print(json.dumps(user_dict, indent=4))
    return user_dict

def pagewise_user_crawler(page):

    query = f"/users?page={page}"
    query_url = baseurl + query

    page_user_list = []

    print(f"Querying Page {page}: ==> " + query_url)
    try:
        response = requests.get(query_url, headers=headers)
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
        with open("log.txt","a") as f:
            f.write(f"Site: {query_url}\n")
            f.write(f"Description: {e}\n")

    print(f"Finished page {page}\n")
    return page_user_list


def batch_page_crawler(page_start, page_end):

    current_batch_users = []
    for page in range(page_start, page_end):
        current_page_users = pagewise_user_crawler(page)
        current_batch_users.extend(current_page_users)

    return current_batch_users

def main():
    os.makedirs('users_data', exist_ok=True)

    # single_user_crawler(sample_user_link)
    # pagewise_user_crawler(1)

    batch_size = 5
    for page in range(1, 10, batch_size):
        page_start = page
        page_end = page + batch_size
        current_batch_users = batch_page_crawler(page_start, page_end)
        with open(f"users_data/users_page{page_start}-page{page_end-1}.json", "w", encoding="utf-8") as f:
            json.dump(current_batch_users, f, indent=4)


if __name__ == "__main__":
    main()
