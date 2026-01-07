
def generate_github_readme(name, interests, learning, collaboration, contact):
    """
    Generate an enhanced GitHub profile README
    
    Args:
        name (str): Your name
        interests (list): List of interests
        learning (str): What you're currently learning
        collaboration (str): What you want to collaborate on
        contact (str): How to reach you
    
    Returns:
        str: Formatted README content
    """
    
    readme_template = f"""# 👋 Hi, I'm {name}

## 🚀 About Me
I'm a passionate technologist with a keen interest in exploring and mastering emerging technologies. Currently diving deep into the world of Python and its applications in modern software development.

## 💡 What I'm Up To
- 🌱 **Currently Learning:** {learning}
- 🤖 **Interests:** {', '.join(interests)}
- 🎯 **Current Goal:** Building an AI-powered document enhancement tool similar to ChatGPT
- 💼 **Looking to Collaborate:** {collaboration}

## 🔧 Technologies & Tools
- **Languages:** Python (learning)
- **Interests:** Generative AI, LLMs, Document Intelligence
- **Focus Areas:** Natural Language Processing, AI-powered productivity tools

## 🌟 Featured Projects
*Coming soon - Building something exciting with generative AI!*

## 💞️ Let's Collaborate
I'm actively seeking collaboration opportunities on:
- Generative AI applications
- Document processing and enhancement tools
- ChatGPT-like conversational AI systems
- Python-based AI/ML projects

## 📫 Get In Touch
- 💬 {contact}
- 🤝 Open to discussions about AI, Python, and innovative tech solutions

---

*"Learning today, building tomorrow"* 🚀
"""
    
    return readme_template


# Example usage
if __name__ == "__main__":
    # Your information
    name = "Adit Kulshreshtha"
    interests = [
        "Generative AI",
        "Machine Learning",
        "Natural Language Processing",
        "Document Intelligence"
    ]
    learning = "Python programming and its ecosystem"
    collaboration = "Open to projects involving generative AI and intelligent document processing"
    contact = "Feel free to reach out - just text me!"
    
    # Generate README
    readme_content = generate_github_readme(
        name=name,
        interests=interests,
        learning=learning,
        collaboration=collaboration,
        contact=contact
    )
    
    # Print the README
    print(readme_content)
    
    # Optionally save to file
    with open("README.md", "w", encoding="utf-8") as f:
        f.write(readme_content)
    
    print("
✅ README.md generated successfully!")

