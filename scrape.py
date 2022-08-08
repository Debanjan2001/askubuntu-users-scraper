from bs4 import BeautifulSoup
import requests
import json

website = 'https://askubuntu.com/users'


sample_user_link = 'https://askubuntu.com/users/231142/terrance'

def user_crawler(site_link):
    
    temp = site_link.split("/")
    user_dict = {
        "user_link": site_link,
        "user_id": temp[-2],
    }

    try:
        response = requests.get(site_link)
        html = response.text
        soup = BeautifulSoup(html, 'html.parser')

        """
        Username
        """
        username = soup.find(class_ = "fs-headline2")
        
        # print(username.get_text().strip())
        user_dict["user_name"] = username.get_text().strip()


        """
        Statistics:
            Reputation, Reach, Answers , Questions, 
        """
        user_stats_field = soup.find(id = 'stats')
        stats = user_stats_field.find_all(class_ = "fs-body3")
        
        # Reputation
        reputation = stats[0].get_text().strip()
        reputation = int(reputation.replace(",", ""))
        # print(reputation)
        user_dict["user_reputation"] = reputation

        # Reach
        reach = stats[1].get_text().strip()
        # print(reach)
        user_dict["user_reach"] = reach

        # Answers
        answers = stats[2].get_text().strip()
        # print(answers)
        user_dict["user_answers"] = answers

         # Questions
        questions = stats[3].get_text().strip()
        # print(questions)
        user_dict["user_questions"] = questions

    except Exception as e:
        print(e)
        with open("log.txt","a") as f:
            f.write(f"Site: {site_link}")
            f.write(f"Description: {e}\n")

    print(json.dumps(user_dict, indent=4))
    return user_dict

def all_user_crawler():

    for page in range(1,2):
        query = f'?page={page}'
        query_url = website + query
        print("Querying ==> " + query_url)
        try:
            response = requests.get(query_url)
            html = response.text
            soup = BeautifulSoup(html, 'html.parser')
            users = soup.find_all(class_="user-info")

            # print(len(users))

        except Exception as e:
            print(e)
            with open("log.txt","a") as f:
                f.write(f"Site: {query_url}")
                f.write(f"Description: {e}\n")
        print(f"Finished page {page}\n")

def main():
    user_crawler(sample_user_link)
    # all_user_crawler()


if __name__ == "__main__":
    main()
