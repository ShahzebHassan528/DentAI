"""
Synthetic dental symptom dataset generator.
~200 sentences per class for 5 conditions.
Classes: cavity, healthy, impacted, infection, other
"""

import json
import random
from pathlib import Path

random.seed(42)

CLASSES = ["cavity", "healthy", "impacted", "infection", "other"]

TEMPLATES = {
    "cavity": [
        "I have sharp pain in my tooth when I eat sweet food.",
        "There is a visible hole in my molar.",
        "My tooth hurts when I drink cold water.",
        "I feel a dull ache in my tooth that comes and goes.",
        "I notice a dark spot on my tooth surface.",
        "There is sensitivity when I bite down on hard food.",
        "My tooth has been aching after eating sugary snacks.",
        "I can feel a rough spot on my tooth with my tongue.",
        "I experience shooting pain in my tooth when exposed to cold air.",
        "My upper molar is very sensitive to sweet and cold drinks.",
        "There is a small pit or hole I can feel in my back tooth.",
        "I have pain that lingers for a few seconds after eating cold food.",
        "My tooth enamel seems to be eroding and I feel sensitivity.",
        "I have intermittent toothache especially after meals.",
        "My dentist said I might have a cavity in my premolar.",
        "I feel pain when I press on a specific tooth.",
        "My tooth has been sensitive to temperature changes.",
        "I have a toothache that gets worse at night.",
        "There is pain in my tooth that started a few days ago.",
        "I notice food getting stuck in a hole in my tooth.",
        "My tooth pain increases when I drink hot tea.",
        "I have a constant dull pain in one of my back teeth.",
        "My tooth sensitivity has been getting worse over weeks.",
        "I feel discomfort in my tooth when I breathe in cold air.",
        "There is a chalky white spot on my tooth that concerns me.",
        "I have pain that radiates from my tooth to my jaw.",
        "My tooth feels rough and the surface looks damaged.",
        "I experience pain when I consume acidic drinks like juice.",
        "My tooth has a cavity that my dentist confirmed last visit.",
        "I feel a sharp sting in my tooth when eating ice cream.",
    ],
    "healthy": [
        "I have no tooth pain and my teeth feel fine.",
        "My teeth and gums look healthy with no issues.",
        "I am here for a routine dental checkup.",
        "My teeth are strong and I have no complaints.",
        "I brush and floss daily and have no dental problems.",
        "I feel no sensitivity or pain in any of my teeth.",
        "My gums are pink and healthy with no bleeding.",
        "I have not experienced any toothache recently.",
        "Everything looks good with my teeth and oral hygiene is great.",
        "My dental X-rays have always come back normal.",
        "I have no cavities or gum issues currently.",
        "My teeth feel clean and strong after regular brushing.",
        "I visit the dentist regularly and have no concerns.",
        "No pain or swelling in my mouth at this time.",
        "I have maintained good oral health for years.",
        "My bite feels comfortable and I have no dental issues.",
        "I have no complaints about my teeth or gums today.",
        "My teeth are well-aligned and I have no dental pain.",
        "I have been taking good care of my teeth and have no problems.",
        "My oral hygiene routine is consistent and effective.",
        "I use fluoride toothpaste and have no sensitivity.",
        "My teeth are clean with no plaque buildup.",
        "I had a dental cleaning recently and everything was fine.",
        "No issues with my teeth and I feel no discomfort.",
        "My dentist confirmed I have no dental problems.",
        "I have healthy teeth and have never needed a filling.",
        "My mouth is completely pain-free.",
        "I have strong enamel and no dental concerns.",
        "My gums do not bleed when I brush or floss.",
        "I have no swelling, pain, or sensitivity in my mouth.",
    ],
    "impacted": [
        "My wisdom tooth is causing severe jaw pain.",
        "I feel pressure and pain at the back of my jaw.",
        "My gum is swollen near my back molar.",
        "I have difficulty fully opening my mouth due to pain.",
        "My wisdom tooth has not fully erupted and is causing discomfort.",
        "I feel a constant pressure behind my last molar.",
        "There is swelling and tenderness at the back of my jaw.",
        "My jaw feels stiff and painful especially in the morning.",
        "I have pain radiating from my jaw to my ear.",
        "My partially erupted wisdom tooth is causing a lot of pain.",
        "I feel pain when I try to open my mouth wide.",
        "My jaw aches and the back of my mouth is swollen.",
        "I have been having recurring pain at the site of my wisdom tooth.",
        "My gum over my impacted tooth is red and inflamed.",
        "I feel pressure and throbbing near my last lower molar.",
        "My wisdom tooth is stuck under the gum and it hurts.",
        "I have pain when chewing that radiates to my jaw.",
        "My jaw feels locked and I cannot open it completely.",
        "There is a persistent ache in the area of my wisdom tooth.",
        "I feel pain when I press around my back upper jaw.",
        "My cheek is slightly swollen near the impacted tooth area.",
        "I have headaches that seem to come from my jaw area.",
        "My wisdom tooth is growing at an angle and causing pain.",
        "I feel pain near my ear that my dentist thinks is from my jaw.",
        "My lower back molar area is very tender to touch.",
        "I have had jaw stiffness for several days now.",
        "The gum around my last tooth is sore and swollen.",
        "I experience a deep aching pain in my jaw that doesn't go away.",
        "My wisdom tooth is pressing against my other teeth causing pain.",
        "I feel discomfort when I bite down near the back of my mouth.",
    ],
    "infection": [
        "I have severe throbbing pain and my face is swollen.",
        "There is a painful bump on my gum that has pus.",
        "I have a fever along with severe toothache.",
        "My jaw and face are swollen on one side.",
        "I have a foul taste in my mouth coming from my tooth.",
        "I can feel an abscess forming near my tooth root.",
        "My tooth pain is unbearable and I have a high temperature.",
        "There is swelling in my cheek along with tooth pain.",
        "I have been experiencing throbbing pain that wakes me at night.",
        "My gum has a pimple-like bump that releases a bad taste.",
        "I have swollen lymph nodes in my neck along with toothache.",
        "My tooth hurts intensely and I feel generally unwell.",
        "There is a bad smell coming from my tooth socket.",
        "I have severe pain and my cheek is visibly swollen.",
        "My infected tooth has been causing headaches and fever.",
        "I have a dental abscess that my dentist diagnosed.",
        "The pain from my tooth has spread to my neck.",
        "I feel pulsating pain in my tooth day and night.",
        "My face is tender to touch and swollen near my tooth.",
        "I have difficulty swallowing due to swelling in my jaw.",
        "There is a bad taste every time I press on my gum.",
        "My tooth pain is so severe I cannot sleep.",
        "I have redness and swelling around my tooth with fever.",
        "My gum around the infected tooth is very painful to touch.",
        "I feel heat and throbbing near my infected molar.",
        "I have swelling that has spread from my jaw to my neck.",
        "There is a constant severe ache in my jaw and tooth.",
        "My tooth pain is accompanied by chills and fatigue.",
        "I have pus draining from my gum near a painful tooth.",
        "My dentist suspects a periapical abscess based on my symptoms.",
    ],
    "other": [
        "I have a cracked tooth that causes pain when I bite.",
        "My filling fell out and the exposed tooth is sensitive.",
        "I have a chipped tooth from an accident.",
        "My gums bleed when I brush and are swollen.",
        "I have been grinding my teeth at night and have jaw pain.",
        "My dental crown feels loose and uncomfortable.",
        "I have pain where my old filling is located.",
        "There is a sore on my gum that has not healed.",
        "My teeth are very sensitive to cold and hot temperatures.",
        "I have gum recession and my teeth roots are exposed.",
        "My tooth was knocked out in a sports injury.",
        "I have persistent bad breath despite good oral hygiene.",
        "My gums are swollen and bleeding regularly.",
        "I have a tooth that is discolored and feels different.",
        "I have bruxism and my teeth feel worn down.",
        "My jaw clicks and pops when I open and close my mouth.",
        "I have pain in my jaw joint that I think is TMJ.",
        "My teeth are very sensitive after whitening treatment.",
        "I have a tooth fracture from biting on hard candy.",
        "My dentures are causing sore spots in my mouth.",
        "I have dry mouth that is affecting my dental health.",
        "My tongue has painful sores that have lasted a week.",
        "I have ulcers in my mouth that are very painful.",
        "My tooth is loose and wiggles when I touch it.",
        "I have sensitivity in multiple teeth after a procedure.",
        "My crown fell off and the tooth underneath is exposed.",
        "I have bleeding gums and my dentist mentioned gingivitis.",
        "My teeth feel rough and uneven on the surface.",
        "I have swelling in my gum that is not painful but noticeable.",
        "My tooth enamel looks worn and my bite has changed.",
    ],
}


def augment_sentences(sentences: list[str], target: int = 200) -> list[str]:
    """Augment by paraphrasing through simple word substitutions."""
    substitutions = {
        "tooth": ["molar", "premolar", "incisor", "tooth"],
        "pain": ["ache", "discomfort", "soreness", "pain"],
        "severe": ["intense", "sharp", "extreme", "terrible", "severe"],
        "swollen": ["inflamed", "puffy", "swollen"],
        "sensitive": ["tender", "sensitive"],
        "have": ["experience", "feel", "notice", "have"],
        "I": ["I"],
        "very": ["quite", "extremely", "very", "really"],
    }

    augmented = list(sentences)
    while len(augmented) < target:
        s = random.choice(sentences)
        words = s.split()
        for i, word in enumerate(words):
            clean = word.lower().rstrip(".,")
            if clean in substitutions:
                replacement = random.choice(substitutions[clean])
                words[i] = word.replace(clean, replacement)
        augmented.append(" ".join(words))

    random.shuffle(augmented)
    return augmented[:target]


def build_dataset(target_per_class: int = 200) -> list[dict]:
    data = []
    for label, cls in enumerate(CLASSES):
        sentences = augment_sentences(TEMPLATES[cls], target=target_per_class)
        for text in sentences:
            data.append({"text": text, "label": label, "class": cls})
    random.shuffle(data)
    return data


def save_dataset(path: Path, target_per_class: int = 200):
    data = build_dataset(target_per_class)
    with open(path, "w") as f:
        json.dump({"classes": CLASSES, "data": data}, f, indent=2)
    print(f"Saved {len(data)} samples to {path}")
    counts = {cls: sum(1 for d in data if d["class"] == cls) for cls in CLASSES}
    for cls, count in counts.items():
        print(f"  {cls}: {count}")
    return data


if __name__ == "__main__":
    out = Path(__file__).parent / "weights" / "symptom_dataset.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    save_dataset(out)
