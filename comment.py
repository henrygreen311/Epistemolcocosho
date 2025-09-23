def make_comment():
    input_file = "gemini.txt"
    output_file = "comment.txt"

    # Define your news hashtags
    hashtags = "#BreakingNews #NewsUpdate #WorldNews #Trending #VXN"

    try:
        # Read original text
        with open(input_file, "r", encoding="utf-8") as f:
            content = f.read().strip()  # remove trailing/leading spaces

        # Build new content with spacing and hashtags
        new_content = f"{content}\n\n{hashtags}\n"

        # Save to comment.txt
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(new_content)

        print(f"✅ File saved as {output_file}")

    except FileNotFoundError:
        print(f"❌ Error: {input_file} not found.")


if __name__ == "__main__":
    make_comment()