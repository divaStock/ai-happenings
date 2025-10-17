"""
Post Storage Module for AI Happenings
Handles persistent storage of LinkedIn posts in JSON and text formats
"""

import json
import os
from datetime import datetime
from typing import Dict, List
from pathlib import Path


class PostStorage:
    """Manages persistent storage of LinkedIn posts."""

    def __init__(self, output_dir: str = "outputs"):
        """
        Initialize post storage.

        Args:
            output_dir: Base directory for storing outputs
        """
        self.output_dir = output_dir
        self.json_dir = os.path.join(output_dir, "json")
        self.text_dir = os.path.join(output_dir, "text")
        self.combined_dir = os.path.join(output_dir, "combined")

        # Create directories if they don't exist
        self._ensure_directories()

    def _ensure_directories(self):
        """Create output directories if they don't exist."""
        for directory in [self.output_dir, self.json_dir, self.text_dir, self.combined_dir]:
            Path(directory).mkdir(parents=True, exist_ok=True)

    def save_posts(self, posts: List[Dict], metadata: Dict = None) -> Dict[str, str]:
        """
        Save posts to both JSON and text formats.

        Args:
            posts: List of post dictionaries
            metadata: Optional metadata about the run

        Returns:
            Dictionary with paths to saved files
        """
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

        # Save JSON
        json_path = self._save_json(posts, metadata, timestamp)

        # Save individual text files
        text_paths = self._save_individual_text_files(posts, timestamp)

        # Save combined text file
        combined_path = self._save_combined_text_file(posts, metadata, timestamp)

        return {
            "json_file": json_path,
            "text_files": text_paths,
            "combined_text_file": combined_path,
            "timestamp": timestamp
        }

    def _save_json(self, posts: List[Dict], metadata: Dict, timestamp: str) -> str:
        """
        Save posts as JSON file.

        Args:
            posts: List of post dictionaries
            metadata: Run metadata
            timestamp: Timestamp string

        Returns:
            Path to saved JSON file
        """
        filename = f"linkedin_posts_{timestamp}.json"
        filepath = os.path.join(self.json_dir, filename)

        data = {
            "generated_at": timestamp,
            "metadata": metadata or {},
            "total_posts": len(posts),
            "posts": posts
        }

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        return filepath

    def _save_individual_text_files(self, posts: List[Dict], timestamp: str) -> List[str]:
        """
        Save each post as individual text file.

        Args:
            posts: List of post dictionaries
            timestamp: Timestamp string

        Returns:
            List of paths to saved text files
        """
        text_paths = []

        # Create subdirectory for this batch
        batch_dir = os.path.join(self.text_dir, f"batch_{timestamp}")
        Path(batch_dir).mkdir(parents=True, exist_ok=True)

        for i, post in enumerate(posts, 1):
            # Create safe filename from title
            title_slug = self._create_slug(post.get("title", f"post_{i}"))
            filename = f"{i:02d}_{title_slug}.txt"
            filepath = os.path.join(batch_dir, filename)

            # Write post content
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(self._format_text_post(post, i))

            text_paths.append(filepath)

        return text_paths

    def _save_combined_text_file(self, posts: List[Dict], metadata: Dict, timestamp: str) -> str:
        """
        Save all posts in a single combined text file.

        Args:
            posts: List of post dictionaries
            metadata: Run metadata
            timestamp: Timestamp string

        Returns:
            Path to combined text file
        """
        filename = f"all_posts_{timestamp}.txt"
        filepath = os.path.join(self.combined_dir, filename)

        with open(filepath, 'w', encoding='utf-8') as f:
            # Write header
            f.write("=" * 80 + "\n")
            f.write("AI HAPPENINGS - LINKEDIN POSTS\n")
            f.write(f"Generated: {timestamp}\n")
            f.write(f"Total Posts: {len(posts)}\n")

            if metadata:
                f.write(f"\nMetadata:\n")
                for key, value in metadata.items():
                    f.write(f"  {key}: {value}\n")

            f.write("=" * 80 + "\n\n")

            # Write each post
            for i, post in enumerate(posts, 1):
                f.write(self._format_text_post(post, i))
                f.write("\n" + "-" * 80 + "\n\n")

        return filepath

    def _format_text_post(self, post: Dict, rank: int) -> str:
        """
        Format a post for text file output.

        Args:
            post: Post dictionary
            rank: Post rank/number

        Returns:
            Formatted text string
        """
        lines = []
        lines.append(f"POST #{rank}")
        lines.append("")
        lines.append(f"Title: {post.get('title', 'N/A')}")
        lines.append(f"Source: {post.get('source', 'N/A')}")
        lines.append(f"Link: {post.get('link', 'N/A')}")
        lines.append(f"Priority Score: {post.get('priority_score', 0)}/100")
        lines.append(f"Relevance Score: {post.get('relevance_score', 0)}/10")
        lines.append("")
        lines.append("LINKEDIN POST:")
        lines.append("-" * 40)
        lines.append(post.get('linkedin_post', 'No post content'))
        lines.append("-" * 40)
        lines.append("")

        return "\n".join(lines)

    def _create_slug(self, text: str, max_length: int = 50) -> str:
        """
        Create URL-safe slug from text.

        Args:
            text: Input text
            max_length: Maximum slug length

        Returns:
            Slugified string
        """
        # Convert to lowercase and replace spaces
        slug = text.lower().strip()
        slug = slug.replace(" ", "_")

        # Remove special characters
        allowed_chars = "abcdefghijklmnopqrstuvwxyz0123456789_-"
        slug = "".join(c for c in slug if c in allowed_chars)

        # Truncate to max length
        return slug[:max_length]

    def get_latest_posts(self, format: str = "json") -> str:
        """
        Get path to the most recent posts file.

        Args:
            format: Format to retrieve ("json", "text", or "combined")

        Returns:
            Path to latest file, or None if no files exist
        """
        if format == "json":
            directory = self.json_dir
            pattern = "linkedin_posts_*.json"
        elif format == "text":
            directory = self.text_dir
            pattern = "batch_*"
        elif format == "combined":
            directory = self.combined_dir
            pattern = "all_posts_*.txt"
        else:
            return None

        # Get all matching files
        path = Path(directory)
        if format == "text":
            files = sorted(path.glob(pattern), key=os.path.getmtime, reverse=True)
        else:
            files = sorted(path.glob(pattern), key=os.path.getmtime, reverse=True)

        return str(files[0]) if files else None

    def load_posts_from_json(self, filepath: str = None) -> Dict:
        """
        Load posts from JSON file.

        Args:
            filepath: Path to JSON file (if None, loads latest)

        Returns:
            Dictionary with posts and metadata
        """
        if filepath is None:
            filepath = self.get_latest_posts("json")
            if filepath is None:
                return {"error": "No saved posts found"}

        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            return {"error": f"Failed to load posts: {str(e)}"}

    def list_saved_runs(self) -> Dict[str, List[str]]:
        """
        List all saved post runs.

        Returns:
            Dictionary with lists of saved files by format
        """
        json_files = sorted(Path(self.json_dir).glob("linkedin_posts_*.json"))
        text_batches = sorted(Path(self.text_dir).glob("batch_*"))
        combined_files = sorted(Path(self.combined_dir).glob("all_posts_*.txt"))

        return {
            "json_files": [str(f) for f in json_files],
            "text_batches": [str(f) for f in text_batches],
            "combined_files": [str(f) for f in combined_files],
            "total_runs": len(json_files)
        }

    def cleanup_old_files(self, keep_last: int = 10):
        """
        Remove old post files, keeping only the most recent ones.

        Args:
            keep_last: Number of recent runs to keep
        """
        # Cleanup JSON files
        json_files = sorted(Path(self.json_dir).glob("linkedin_posts_*.json"),
                           key=os.path.getmtime, reverse=True)
        for filepath in json_files[keep_last:]:
            filepath.unlink()

        # Cleanup text batch directories
        text_batches = sorted(Path(self.text_dir).glob("batch_*"),
                             key=os.path.getmtime, reverse=True)
        for dirpath in text_batches[keep_last:]:
            for file in dirpath.iterdir():
                file.unlink()
            dirpath.rmdir()

        # Cleanup combined text files
        combined_files = sorted(Path(self.combined_dir).glob("all_posts_*.txt"),
                               key=os.path.getmtime, reverse=True)
        for filepath in combined_files[keep_last:]:
            filepath.unlink()

    def get_storage_stats(self) -> Dict:
        """
        Get statistics about stored posts.

        Returns:
            Dictionary with storage statistics
        """
        json_files = list(Path(self.json_dir).glob("linkedin_posts_*.json"))
        text_batches = list(Path(self.text_dir).glob("batch_*"))
        combined_files = list(Path(self.combined_dir).glob("all_posts_*.txt"))

        # Calculate total size
        total_size = 0
        for filepath in json_files + combined_files:
            total_size += filepath.stat().st_size

        for dirpath in text_batches:
            for file in dirpath.iterdir():
                total_size += file.stat().st_size

        return {
            "total_runs": len(json_files),
            "json_files_count": len(json_files),
            "text_batches_count": len(text_batches),
            "combined_files_count": len(combined_files),
            "total_size_bytes": total_size,
            "total_size_mb": round(total_size / (1024 * 1024), 2)
        }
