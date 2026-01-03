"""
Training Data Analyzer & Filter
Analyzes 63k messages and selects best subset for training
"""
import json
import os
from pathlib import Path
from collections import Counter
from datetime import datetime
import re

class TrainingDataAnalyzer:
    def __init__(self, data_path: str):
        self.data_path = Path(data_path)
        self.messages = []
        self.stats = {}
        
    def load_messages(self):
        """Load messages from JSONL file"""
        print("📂 Loading messages...")
        with open(self.data_path, 'r', encoding='utf-8') as f:
            for line in f:
                try:
                    msg = json.loads(line)
                    self.messages.append(msg)
                except json.JSONDecodeError:
                    continue
        print(f"✅ Loaded {len(self.messages):,} messages")
        
    def analyze_dataset(self):
        """Generate comprehensive statistics"""
        print("\n📊 Analyzing dataset...")
        
        total = len(self.messages)
        authors = Counter()
        lengths = []
        has_reactions = 0
        has_replies = 0
        has_urls = 0
        has_mentions = 0
        bot_messages = 0
        
        for msg in self.messages:
            # Author distribution
            authors[msg.get('author_name', 'Unknown')] += 1
            
            # Length statistics
            content = msg.get('content', '')
            lengths.append(len(content))
            
            # Engagement metrics
            if msg.get('reactions', 0) > 0:
                has_reactions += 1
            if msg.get('reply_count', 0) > 0:
                has_replies += 1
            if 'http' in content.lower():
                has_urls += 1
            if '@' in content:
                has_mentions += 1
            if msg.get('is_bot', False):
                bot_messages += 1
        
        self.stats = {
            'total_messages': total,
            'unique_authors': len(authors),
            'top_authors': authors.most_common(5),
            'avg_length': sum(lengths) / len(lengths) if lengths else 0,
            'min_length': min(lengths) if lengths else 0,
            'max_length': max(lengths) if lengths else 0,
            'with_reactions': has_reactions,
            'with_replies': has_replies,
            'with_urls': has_urls,
            'with_mentions': has_mentions,
            'bot_messages': bot_messages,
        }
        
        self.print_stats()
        
    def print_stats(self):
        """Print analysis results"""
        s = self.stats
        print("\n" + "="*60)
        print("📈 DATASET ANALYSIS")
        print("="*60)
        print(f"Total Messages:        {s['total_messages']:,}")
        print(f"Unique Authors:        {s['unique_authors']}")
        print(f"Bot Messages:          {s['bot_messages']:,} ({s['bot_messages']/s['total_messages']*100:.1f}%)")
        print(f"\nTop 5 Authors:")
        for author, count in s['top_authors']:
            print(f"  - {author}: {count:,} ({count/s['total_messages']*100:.1f}%)")
        print(f"\nMessage Lengths:")
        print(f"  Average: {s['avg_length']:.1f} characters")
        print(f"  Min: {s['min_length']}, Max: {s['max_length']}")
        print(f"\nEngagement Metrics:")
        print(f"  With reactions: {s['with_reactions']:,} ({s['with_reactions']/s['total_messages']*100:.1f}%)")
        print(f"  With replies: {s['with_replies']:,} ({s['with_replies']/s['total_messages']*100:.1f}%)")
        print(f"  With URLs: {s['with_urls']:,} ({s['with_urls']/s['total_messages']*100:.1f}%)")
        print(f"  With mentions: {s['with_mentions']:,} ({s['with_mentions']/s['total_messages']*100:.1f}%)")
        print("="*60)
        
    def calculate_message_score(self, msg: dict) -> float:
        """Score message quality (0-100)"""
        score = 50.0  # Base score
        
        content = msg.get('content', '')
        length = len(content)
        
        # Length score (sweet spot: 50-300 chars)
        if 50 <= length <= 300:
            score += 15
        elif 30 <= length < 50 or 300 < length <= 500:
            score += 10
        elif length < 30:
            score += 5
        else:
            score += 0
            
        # Engagement score
        reactions = msg.get('reactions', 0)
        replies = msg.get('reply_count', 0)
        score += min(reactions * 5, 15)  # Max +15 for reactions
        score += min(replies * 3, 10)    # Max +10 for replies
        
        # Content quality indicators
        if not msg.get('is_bot', False):
            score += 10  # Prefer human messages
        
        # Personality indicators (adjust for your bot)
        personality_markers = [
            r'\b(lol|lmao|haha|lmfao)\b',  # Humor
            r'[!?]{2,}',                    # Emphasis
            r'\b(honestly|literally|tbh)\b', # Conversational
        ]
        for pattern in personality_markers:
            if re.search(pattern, content, re.IGNORECASE):
                score += 3
        
        # Penalties
        if 'http' in content.lower():
            score -= 5  # URLs less useful for personality
        if length < 10:
            score -= 10  # Too short
        if msg.get('is_bot', False):
            score -= 15  # Bot messages less useful
            
        return max(0, min(100, score))
    
    def filter_messages(self, target_count: int = 10000, min_score: float = 60.0):
        """Filter to best quality messages"""
        print(f"\n🔍 Filtering to top {target_count:,} messages (min score: {min_score})...")
        
        # Score all messages
        scored_messages = []
        for msg in self.messages:
            score = self.calculate_message_score(msg)
            if score >= min_score:
                scored_messages.append((score, msg))
        
        print(f"✅ {len(scored_messages):,} messages above threshold")
        
        # Sort by score and take top N
        scored_messages.sort(reverse=True, key=lambda x: x[0])
        top_messages = [msg for score, msg in scored_messages[:target_count]]
        
        print(f"📦 Selected top {len(top_messages):,} messages")
        return top_messages
    
    def estimate_training_time(self, num_messages: int, epochs: int = 3):
        """Estimate training time"""
        batch_size = 1
        grad_accum = 16
        time_per_step = 30  # seconds on RTX 2080 Ti
        
        effective_batch = batch_size * grad_accum
        steps_per_epoch = num_messages // effective_batch
        total_steps = steps_per_epoch * epochs
        total_seconds = total_steps * time_per_step
        
        hours = total_seconds / 3600
        days = hours / 24
        
        print(f"\n⏱️  TRAINING TIME ESTIMATE")
        print(f"{'='*60}")
        print(f"Messages:              {num_messages:,}")
        print(f"Epochs:                {epochs}")
        print(f"Effective batch size:  {effective_batch}")
        print(f"Steps per epoch:       {steps_per_epoch:,}")
        print(f"Total steps:           {total_steps:,}")
        print(f"─────────────────────────────────────────────────────────")
        print(f"Estimated time:        {hours:.1f} hours ({days:.1f} days)")
        print(f"{'='*60}\n")
        
        return hours
    
    def save_filtered_data(self, messages: list, output_path: str):
        """Save filtered messages to new file"""
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        print(f"💾 Saving to {output_path}...")
        with open(output_path, 'w', encoding='utf-8') as f:
            for msg in messages:
                f.write(json.dumps(msg) + '\n')
        print(f"✅ Saved {len(messages):,} messages")


def main():
    """Main execution"""
    print("="*60)
    print("🤖 TRAINING DATA ANALYZER")
    print("="*60)
    
    # Configuration
    input_file = "./data/training_data.jsonl"
    output_file = "./data/training_data_filtered.jsonl"
    
    # Check if file exists
    if not Path(input_file).exists():
        print(f"❌ File not found: {input_file}")
        print("Run backfill_messages.py first to collect data.")
        return
    
    # Initialize analyzer
    analyzer = TrainingDataAnalyzer(input_file)
    analyzer.load_messages()
    analyzer.analyze_dataset()
    
    # Estimate time for full dataset
    print("\n" + "─"*60)
    print("📊 SCENARIO 1: Train on ALL messages")
    print("─"*60)
    full_time = analyzer.estimate_training_time(len(analyzer.messages), epochs=3)
    
    # Estimate time for filtered dataset
    print("\n" + "─"*60)
    print("📊 SCENARIO 2: Train on FILTERED messages (recommended)")
    print("─"*60)
    
    # Try different filter sizes
    target_sizes = [5000, 10000, 15000]
    for size in target_sizes:
        if size <= len(analyzer.messages):
            print(f"\n→ Target: {size:,} messages")
            filtered_time = analyzer.estimate_training_time(size, epochs=3)
            time_saved = full_time - filtered_time
            print(f"   Time saved: {time_saved:.1f} hours ({time_saved/24:.1f} days)")
    
    # Ask user for filtering
    print("\n" + "="*60)
    choice = input("\nFilter dataset? [y/N]: ").strip().lower()
    
    if choice == 'y':
        try:
            target = int(input("Target size (e.g., 10000): ").strip() or "10000")
            min_score = float(input("Min quality score 0-100 (default: 60): ").strip() or "60")
            
            filtered = analyzer.filter_messages(target_count=target, min_score=min_score)
            analyzer.save_filtered_data(filtered, output_file)
            
            print(f"\n✅ Done! Use this file for training:")
            print(f"   {output_file}")
            print(f"\nUpdate .env:")
            print(f"   TRAINING_DATA_PATH={output_file}")
            
        except ValueError as e:
            print(f"❌ Invalid input: {e}")
    else:
        print("\n👍 Keeping full dataset")
        print("Note: Training will take ~4-5 days on RTX 2080 Ti")


if __name__ == "__main__":
    main()
