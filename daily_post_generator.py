import os
import pathlib
import google.generativeai as genai
from datetime import datetime
import re

# --- Configuration ---
API_KEY = os.getenv("GEMINI_API_KEY")
PROMPTS_PAGE_URL = "/prompts" # Assuming this is the correct URL

# This is the prompt that will be sent to Gemini.
# Please review and let me know if you want to change it.
GENERATION_PROMPT = """
You are an AI named Gemini, and you are the author of a blog called "UnSuper-Vized".

Your task is to write a new blog post that is between 500 and 1000 words.

The post must have a clear, engaging title and end with a section titled "**The Moral of the Story**".

Today's post should cover the most recent news posted about generative AI.

Review the previous post on the blog and apply the lesson learned on today's post, ensuring you mention where you applied it.

The output must be formatted as follows:
- The first line must be the title of the blog post.
- The rest of the content must be the body of the blog post, written in Markdown.
- Do not include the front matter (like `---` or `title:`). The script will add it.
"""

def generate_filename_from_title(title):
    """Generates a slug-like filename from a title."""
    # Remove special characters, replace spaces with hyphens, and convert to lowercase
    slug = re.sub(r'[^a-zA-Z0-9\s-]', '', title).strip().replace(' ', '-')
    return f"{slug}.md"

def main():
    """Generates and saves a new blog post."""
    if not API_KEY:
        print("Error: GEMINI_API_KEY environment variable not set.")
        return

    print("Connecting to Google AI Studio...")
    genai.configure(api_key=API_KEY)
    model = genai.GenerativeModel('gemini-pro')

    print("Generating new blog post...")
    response = model.generate_content(GENERATION_PROMPT)
    
    try:
        # Split the response to get title and content
        parts = response.text.strip().split('\n', 1)
        title = parts[0]
        content = parts[1].strip()

        # Create the intro block
        intro_block = (
            f'> *This post was generated from the following prompt: `{GENERATION_PROMPT.strip()}`*\n'
            f'> \n'
            f'> *You can see the full list of prompts for this site on the [Prompts page]({PROMPTS_PAGE_URL}).*\n\n'
            '---\n\n'
        )

        full_content = intro_block + content
        
        # Create the front matter
        today = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S+00:00')
        front_matter = (
            f"---\n"
            f"title: \"{title}\"\n"
            f"date: {today}\n"
            f"draft: false\n"
            f"author: \"Gemini\"\n"
            f"---\n\n"
        )

        # Assemble the final file content
        final_file_content = front_matter + full_content

        # Generate filename and save the file
        filename = generate_filename_from_title(title)
        blog_dir = pathlib.Path(__file__).parent / "content" / "blog"
        blog_dir.mkdir(exist_ok=True)
        filepath = blog_dir / filename

        print(f"Saving new post to: {filepath}")
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(final_file_content)
        
        print("Blog post generated successfully.")

    except (IndexError, AttributeError) as e:
        print(f"Error: Could not parse the response from the API.")
        print(f"API Response was:\n---\n{response.text}\n---")
        print(f"Error details: {e}")


if __name__ == "__main__":
    main()
