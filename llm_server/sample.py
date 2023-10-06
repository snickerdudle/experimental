import requests


def main():
    header = "Please answer the question below. Be as concise and precise as possible.\n\n"

    prompt = """
Design a detailed outline for a multi-disciplinary research paper titled "Interplay of Quantum Computing, Artificial Intelligence, and Climate Change: Opportunities and Challenges for the 21st Century". Your outline should be divided into:

Introduction
Main Body (with at least three subsections)
Conclusion
Future Recommendations
For each section and subsection, provide a 2-3 sentence description of the content. Also, highlight three key points or findings that would be covered in each subsection."""

    # Send the prompt via POST to localhost:5000/prompt
    response = requests.post(
        url="http://localhost:5000/prompt",
        data={"prompt": prompt},
    )

    # Print the response
    print(response.json()["output"])


if __name__ == "__main__":
    main()
