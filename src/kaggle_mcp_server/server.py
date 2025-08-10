#!/usr/bin/env python3
"""
Kaggle MCP Server

A Model Context Protocol server that provides access to Kaggle's API functionality,
including competitions, datasets, notebooks, and models.
"""

import logging
from typing import Any, Dict, Optional
from pathlib import Path

from mcp.server.fastmcp import FastMCP
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize MCP server
mcp = FastMCP("Kaggle MCP Server")

# Global Kaggle API instance
kaggle_api: Optional[Any] = None


def safe_serialize(obj: Any) -> Any:
    """Safely serialize Kaggle API objects to JSON-compatible format."""
    if obj is None:
        return None

    # Handle primitive types
    if isinstance(obj, (str, int, float, bool)):
        return obj

    # Handle lists and tuples
    if isinstance(obj, (list, tuple)):
        return [safe_serialize(item) for item in obj]

    # Handle dictionaries
    if isinstance(obj, dict):
        return {key: safe_serialize(value) for key, value in obj.items()}

    # Handle datetime objects
    if hasattr(obj, "isoformat"):
        return obj.isoformat()

    # Handle objects with name attribute (like enums)
    if hasattr(obj, "name"):
        return obj.name

    # Handle objects with value attribute
    if hasattr(obj, "value"):
        return obj.value

    # Convert to string as fallback
    return str(obj)


def initialize_kaggle_api() -> Any:
    """Initialize and authenticate Kaggle API client."""
    global kaggle_api

    if kaggle_api is None:
        try:
            from kaggle.api.kaggle_api_extended import KaggleApi

            kaggle_api = KaggleApi()
            kaggle_api.authenticate()
            logger.info("Kaggle API authenticated successfully")
        except Exception as e:
            logger.error(f"Failed to authenticate Kaggle API: {e}")
            raise

    return kaggle_api


@mcp.tool(description="List active Kaggle competitions with optional filtering")
def list_competitions(
    search: str = "",
    category: str = "all",
    sort_by: str = "deadline",
    page: int = 1,
    page_size: int = 20,
) -> Dict[str, Any]:
    """
    List Kaggle competitions with filtering options.

    Args:
        search: Search term to filter competitions
        category: Competition category (all, featured, research, recruitment, etc.)
        sort_by: Sort order (deadline, prize, numberOfTeams, recentlyCreated)
        page: Page number for pagination
        page_size: Number of competitions per page

    Returns:
        Dictionary containing competition list and metadata
    """
    try:
        api = initialize_kaggle_api()

        # Get competitions list
        competitions = api.competitions_list()

        # Format response
        result = {
            "competitions": [],
            "total_count": len(competitions),
            "page": page,
            "page_size": page_size,
        }

        for comp in competitions:
            comp_data = {
                "id": safe_serialize(comp.id),
                "title": safe_serialize(comp.title),
                "url": safe_serialize(comp.url),
                "description": safe_serialize(comp.description),
                "category": safe_serialize(getattr(comp, "category", None)),
                "reward": safe_serialize(comp.reward),
                "deadline": safe_serialize(comp.deadline),
                "max_team_size": safe_serialize(getattr(comp, "maxTeamSize", None)),
                "evaluation_metric": safe_serialize(
                    getattr(comp, "evaluationMetric", None)
                ),
                "total_teams": safe_serialize(getattr(comp, "totalTeams", None)),
                "user_has_entered": safe_serialize(
                    getattr(comp, "userHasEntered", None)
                ),
            }
            result["competitions"].append(comp_data)

        return result

    except Exception as e:
        logger.error(f"Error listing competitions: {e}")
        return {"error": str(e), "competitions": []}


@mcp.tool(description="Get detailed information about a specific Kaggle competition")
def get_competition_details(competition_id: str) -> Dict[str, Any]:
    """
    Get detailed information about a specific competition.

    Args:
        competition_id: The competition identifier

    Returns:
        Dictionary containing detailed competition information
    """
    try:
        api = initialize_kaggle_api()

        # Get competition details
        competitions = api.competitions_list()
        competition = next(
            (
                c
                for c in competitions
                if str(c.id) == str(competition_id) 
                or c.id == competition_id
                or getattr(c, 'ref', '') == competition_id
                or getattr(c, 'url', '').endswith(f'/{competition_id}')
            ),
            None,
        )
        if not competition:
            return {"error": f"Competition {competition_id} not found"}

        # Format response
        result = {
            "id": safe_serialize(competition.id),
            "title": safe_serialize(competition.title),
            "url": safe_serialize(competition.url),
            "description": safe_serialize(competition.description),
            "category": safe_serialize(getattr(competition, "category", None)),
            "reward": safe_serialize(competition.reward),
            "deadline": safe_serialize(competition.deadline),
            "max_team_size": safe_serialize(getattr(competition, "maxTeamSize", None)),
            "evaluation_metric": safe_serialize(
                getattr(competition, "evaluationMetric", None)
            ),
            "total_teams": safe_serialize(getattr(competition, "totalTeams", None)),
            "user_has_entered": safe_serialize(
                getattr(competition, "userHasEntered", None)
            ),
            "tags": safe_serialize(getattr(competition, "tags", [])),
            "timeline": {
                "start_date": safe_serialize(getattr(competition, "enabledDate", None)),
                "deadline": safe_serialize(competition.deadline),
                "evaluation_end_date": safe_serialize(
                    getattr(competition, "evaluationEndDate", None)
                ),
            },
        }

        return result

    except Exception as e:
        logger.error(f"Error getting competition details: {e}")
        return {"error": str(e)}


@mcp.tool(description="Download competition files to a specified directory")
def download_competition_files(
    competition_id: str,
    download_path: str = "./kaggle_data",
    file_name: Optional[str] = None,
    force: bool = False,
    quiet: bool = True,
) -> Dict[str, Any]:
    """
    Download files from a Kaggle competition.

    Args:
        competition_id: The competition identifier
        download_path: Local directory to download files to
        file_name: Specific file to download (optional, downloads all if not specified)
        force: Force download even if files exist
        quiet: Suppress download progress output

    Returns:
        Dictionary containing download status and file information
    """
    try:
        api = initialize_kaggle_api()

        # Create download directory
        Path(download_path).mkdir(parents=True, exist_ok=True)

        # Download files
        if file_name:
            api.competition_download_file(
                competition=competition_id,
                file_name=file_name,
                path=download_path,
                force=force,
                quiet=quiet,
            )
            downloaded_files = [file_name]
        else:
            api.competition_download_files(
                competition=competition_id, path=download_path, force=force, quiet=quiet
            )
            # List downloaded files
            download_dir = Path(download_path) / competition_id
            downloaded_files = (
                [f.name for f in download_dir.iterdir() if f.is_file()]
                if download_dir.exists()
                else []
            )

        return {
            "status": "success",
            "competition_id": competition_id,
            "download_path": download_path,
            "downloaded_files": downloaded_files,
            "total_files": len(downloaded_files),
        }

    except Exception as e:
        logger.error(f"Error downloading competition files: {e}")
        return {"error": str(e), "status": "failed"}


@mcp.tool(description="Search for Kaggle datasets with filtering options")
def search_datasets(
    search: str = "",
    sort_by: str = "hottest",
    size: str = "all",
    file_type: str = "all",
    license_name: str = "all",
    tag_ids: str = "",
    user: str = "",
    page: int = 1,
    page_size: int = 20,
) -> Dict[str, Any]:
    """
    Search for Kaggle datasets with various filtering options.

    Args:
        search: Search term
        sort_by: Sort order (hottest, votes, updated, active, published)
        size: Dataset size filter (all, small, medium, large)
        file_type: File type filter (all, csv, sqlite, json, etc.)
        license_name: License filter (all, cc, mit, other, etc.)
        tag_ids: Comma-separated tag IDs
        user: Filter by username
        page: Page number for pagination
        page_size: Number of datasets per page

    Returns:
        Dictionary containing dataset search results
    """
    try:
        api = initialize_kaggle_api()

        # Prepare search parameters
        search_params = {
            "search": search if search else None,
            "sort_by": sort_by,
            "size": size if size != "all" else None,
            "file_type": file_type if file_type != "all" else None,
            "license_name": license_name if license_name != "all" else None,
            "tag_ids": tag_ids if tag_ids else None,
            "user": user if user else None,
            "page": page,
            "page_size": page_size,
        }

        # Remove None values
        search_params = {k: v for k, v in search_params.items() if v is not None}

        # Search datasets
        datasets = api.dataset_list()

        # Format response
        result = {
            "datasets": [],
            "total_count": len(datasets),
            "page": page,
            "page_size": page_size,
        }

        for dataset in datasets:
            dataset_data = {
                "ref": safe_serialize(getattr(dataset, "ref", None)),
                "title": safe_serialize(getattr(dataset, "title", None)),
                "size": safe_serialize(getattr(dataset, "size", None)),
                "last_updated": safe_serialize(getattr(dataset, "lastUpdated", None)),
                "download_count": safe_serialize(
                    getattr(dataset, "downloadCount", None)
                ),
                "vote_count": safe_serialize(getattr(dataset, "voteCount", None)),
                "usability_rating": safe_serialize(
                    getattr(dataset, "usabilityRating", None)
                ),
                "license_name": safe_serialize(getattr(dataset, "licenseName", None)),
                "tags": safe_serialize(getattr(dataset, "tags", [])),
                "url": f"https://www.kaggle.com/datasets/{safe_serialize(getattr(dataset, 'ref', ''))}",
            }
            result["datasets"].append(dataset_data)

        return result

    except Exception as e:
        logger.error(f"Error searching datasets: {e}")
        return {"error": str(e), "datasets": []}


@mcp.tool(description="Get detailed information about a specific Kaggle dataset")
def get_dataset_details(dataset_ref: str) -> Dict[str, Any]:
    """
    Get detailed information about a specific dataset.

    Args:
        dataset_ref: Dataset reference in format 'username/dataset-name'

    Returns:
        Dictionary containing detailed dataset information
    """
    try:
        api = initialize_kaggle_api()

        # Split dataset reference
        if "/" not in dataset_ref:
            return {
                "error": "Invalid dataset reference format. Use 'username/dataset-name'"
            }

        owner_slug, dataset_slug = dataset_ref.split("/", 1)

        # Get dataset metadata
        dataset = api.dataset_view(owner_slug, dataset_slug)

        # Get dataset files
        files = api.dataset_list_files(owner_slug, dataset_slug)

        # Format response
        result = {
            "ref": dataset.ref,
            "title": dataset.title,
            "description": dataset.description,
            "size": dataset.size,
            "last_updated": dataset.lastUpdated.isoformat()
            if dataset.lastUpdated
            else None,
            "download_count": dataset.downloadCount,
            "vote_count": dataset.voteCount,
            "usability_rating": dataset.usabilityRating,
            "license_name": dataset.licenseName,
            "tags": dataset.tags if hasattr(dataset, "tags") else [],
            "url": f"https://www.kaggle.com/datasets/{dataset.ref}",
            "files": [],
        }

        for file in files:
            file_data = {
                "name": file.name,
                "size": file.size,
                "creation_date": file.creationDate.isoformat()
                if file.creationDate
                else None,
            }
            result["files"].append(file_data)

        return result

    except Exception as e:
        logger.error(f"Error getting dataset details: {e}")
        return {"error": str(e)}


@mcp.tool(description="Download a Kaggle dataset to a specified directory")
def download_dataset(
    dataset_ref: str,
    download_path: str = "./kaggle_data",
    file_name: Optional[str] = None,
    force: bool = False,
    quiet: bool = True,
    unzip: bool = True,
) -> Dict[str, Any]:
    """
    Download a Kaggle dataset.

    Args:
        dataset_ref: Dataset reference in format 'username/dataset-name'
        download_path: Local directory to download files to
        file_name: Specific file to download (optional)
        force: Force download even if files exist
        quiet: Suppress download progress output
        unzip: Automatically unzip downloaded files

    Returns:
        Dictionary containing download status and file information
    """
    try:
        api = initialize_kaggle_api()

        # Split dataset reference
        if "/" not in dataset_ref:
            return {
                "error": "Invalid dataset reference format. Use 'username/dataset-name'"
            }

        owner_slug, dataset_slug = dataset_ref.split("/", 1)

        # Create download directory
        Path(download_path).mkdir(parents=True, exist_ok=True)

        # Download dataset
        if file_name:
            api.dataset_download_file(
                owner_slug=owner_slug,
                dataset_slug=dataset_slug,
                file_name=file_name,
                path=download_path,
                force=force,
                quiet=quiet,
            )
            downloaded_files = [file_name]
        else:
            api.dataset_download_files(
                owner_slug=owner_slug,
                dataset_slug=dataset_slug,
                path=download_path,
                force=force,
                quiet=quiet,
                unzip=unzip,
            )
            # List downloaded files
            dataset_dir = Path(download_path) / dataset_slug
            downloaded_files = (
                [f.name for f in dataset_dir.iterdir() if f.is_file()]
                if dataset_dir.exists()
                else []
            )

        return {
            "status": "success",
            "dataset_ref": dataset_ref,
            "download_path": download_path,
            "downloaded_files": downloaded_files,
            "total_files": len(downloaded_files),
        }

    except Exception as e:
        logger.error(f"Error downloading dataset: {e}")
        return {"error": str(e), "status": "failed"}


@mcp.tool(description="List Kaggle models with filtering options")
def list_models(
    search: str = "",
    sort_by: str = "hottest",
    owner: str = "",
    page: int = 1,
    page_size: int = 20,
) -> Dict[str, Any]:
    """
    List Kaggle models with filtering options.

    Args:
        search: Search term to filter models
        sort_by: Sort order (hottest, downloadCount, voteCount, createTime)
        owner: Filter by model owner
        page: Page number for pagination
        page_size: Number of models per page

    Returns:
        Dictionary containing model list and metadata
    """
    try:
        api = initialize_kaggle_api()

        # Get models list
        models = api.model_list(
            search=search if search else None,
            sort_by="hotness",
            owner=owner if owner else None,
            page_size=page_size,
            page_token=str(page) if page > 1 else None,
        )

        # Format response
        result = {
            "models": [],
            "total_count": len(models),
            "page": page,
            "page_size": page_size,
        }

        for model in models:
            model_data = {
                "ref": getattr(model, "ref", None),
                "title": getattr(model, "title", None),
                "subtitle": getattr(model, "subtitle", None),
                "author": getattr(model, "author", None),
                "slug": getattr(model, "slug", None),
                "is_private": getattr(model, "isPrivate", None),
                "description": getattr(model, "description", None),
                "publish_time": getattr(model, "publishTime", None).isoformat()
                if hasattr(model, "publishTime") and model.publishTime
                else None,
                "url": f"https://www.kaggle.com/models/{getattr(model, 'ref', '')}",
            }
            result["models"].append(model_data)

        return result

    except Exception as e:
        logger.error(f"Error listing models: {e}")
        return {"error": str(e), "models": []}


@mcp.resource("kaggle://competitions/active")
def get_active_competitions() -> str:
    """Get currently active competitions as a resource."""
    try:
        api = initialize_kaggle_api()
        competitions = api.competitions_list()

        # Filter active competitions
        active_comps = [
            comp
            for comp in competitions
            if not comp.deadline or comp.deadline > comp.deadline.now()
        ]

        result = "# Active Kaggle Competitions\n\n"
        for comp in active_comps[:20]:  # Limit to top 20
            result += f"## {comp.title}\n"
            result += f"- **ID**: {comp.id}\n"
            result += f"- **Category**: {comp.category}\n"
            result += f"- **Reward**: {comp.reward}\n"
            result += f"- **Deadline**: {comp.deadline.isoformat() if comp.deadline else 'Not specified'}\n"
            result += f"- **Teams**: {comp.totalTeams}\n"
            result += f"- **URL**: {comp.url}\n\n"

        return result

    except Exception as e:
        logger.error(f"Error getting active competitions resource: {e}")
        return f"Error: {str(e)}"


@mcp.resource("kaggle://datasets/popular")
def get_popular_datasets() -> str:
    """Get popular datasets as a resource."""
    try:
        api = initialize_kaggle_api()
        datasets = api.dataset_list()

        result = "# Popular Kaggle Datasets\n\n"
        for dataset in datasets:
            result += f"## {dataset.title}\n"
            result += f"- **Reference**: {dataset.ref}\n"
            result += f"- **Size**: {dataset.size}\n"
            result += f"- **Downloads**: {dataset.downloadCount}\n"
            result += f"- **Votes**: {dataset.voteCount}\n"
            result += f"- **Usability**: {dataset.usabilityRating}\n"
            result += f"- **License**: {dataset.licenseName}\n"
            result += f"- **Last Updated**: {dataset.lastUpdated.isoformat() if dataset.lastUpdated else 'Unknown'}\n"
            result += f"- **URL**: https://www.kaggle.com/datasets/{dataset.ref}\n\n"

        return result

    except Exception as e:
        logger.error(f"Error getting popular datasets resource: {e}")
        return f"Error: {str(e)}"


@mcp.resource("kaggle://trends/hot-topics")
def get_hot_topics() -> str:
    """Get trending topics and techniques as a resource."""
    try:
        api = initialize_kaggle_api()
        
        # Get recent competitions to analyze trends
        competitions = api.competitions_list()
        datasets = api.dataset_list()
        
        result = "# Trending Topics & Techniques on Kaggle\n\n"
        
        # Analyze competition categories
        result += "## 🔥 Hot Competition Categories\n\n"
        categories = {}
        for comp in competitions[:20]:
            category = getattr(comp, 'category', 'Unknown')
            if category in categories:
                categories[category] += 1
            else:
                categories[category] = 1
        
        for category, count in sorted(categories.items(), key=lambda x: x[1], reverse=True):
            result += f"- **{category}**: {count} active competitions\n"
        
        # Recent high-value competitions
        result += "\n## 💰 High-Value Recent Competitions\n\n"
        high_value_comps = [comp for comp in competitions if 'Usd' in comp.reward and comp.reward != 'Knowledge']
        for comp in high_value_comps[:5]:
            result += f"- **{comp.title}**: {comp.reward}\n"
        
        # Popular dataset types
        result += "\n## 📊 Trending Dataset Types\n\n"
        dataset_sizes = {'Small': 0, 'Medium': 0, 'Large': 0}
        for dataset in datasets[:50]:
            if hasattr(dataset, 'size'):
                if 'KB' in str(dataset.size) or ('MB' in str(dataset.size) and float(str(dataset.size).split()[0]) < 10):
                    dataset_sizes['Small'] += 1
                elif 'MB' in str(dataset.size):
                    dataset_sizes['Medium'] += 1
                else:
                    dataset_sizes['Large'] += 1
        
        for size_type, count in dataset_sizes.items():
            result += f"- **{size_type} Datasets**: {count} popular entries\n"
        
        result += "\n## 🚀 Emerging Patterns\n\n"
        result += "- **AI/ML Focus**: General artificial intelligence challenges gaining traction\n"
        result += "- **Real-world Impact**: More competitions focusing on social good\n"
        result += "- **Multi-modal Data**: Increasing use of combined text, image, and sensor data\n"
        result += "- **Time Series**: Growing interest in forecasting and temporal data\n"
        
        return result

    except Exception as e:
        logger.error(f"Error getting hot topics resource: {e}")
        return f"Error: {str(e)}"


@mcp.resource("kaggle://calendar/deadlines")
def get_upcoming_deadlines() -> str:
    """Get upcoming competition deadlines as a resource."""
    try:
        api = initialize_kaggle_api()
        competitions = api.competitions_list()
        
        from datetime import datetime, timedelta
        now = datetime.now()
        
        result = "# Upcoming Competition Deadlines\n\n"
        
        # Filter competitions with deadlines in the next 60 days
        upcoming = []
        for comp in competitions:
            if hasattr(comp, 'deadline') and comp.deadline:
                try:
                    # Try to parse deadline
                    if hasattr(comp.deadline, 'replace'):
                        deadline = comp.deadline
                    else:
                        continue
                    
                    days_until = (deadline - now).days
                    if 0 <= days_until <= 60:
                        upcoming.append((comp, days_until))
                except:
                    continue
        
        # Sort by deadline
        upcoming.sort(key=lambda x: x[1])
        
        result += "## ⏰ Next 30 Days\n\n"
        for comp, days in upcoming[:10]:
            if days <= 30:
                urgency = "🔥 URGENT" if days <= 7 else "⚡ Soon"
                result += f"- **{comp.title}** ({urgency})\n"
                result += f"  - Days left: {days}\n"
                result += f"  - Reward: {comp.reward}\n"
                result += f"  - Deadline: {comp.deadline.strftime('%Y-%m-%d %H:%M')}\n\n"
        
        result += "## 📅 This Month\n\n"
        for comp, days in upcoming:
            if 30 < days <= 60:
                result += f"- **{comp.title}**\n"
                result += f"  - Days left: {days}\n"
                result += f"  - Reward: {comp.reward}\n\n"
        
        return result

    except Exception as e:
        logger.error(f"Error getting deadlines resource: {e}")
        return f"Error: {str(e)}"


@mcp.resource("kaggle://beginner/getting-started")
def get_beginner_guide() -> str:
    """Get beginner-friendly resources and learning path."""
    try:
        api = initialize_kaggle_api()
        competitions = api.competitions_list()
        datasets = api.dataset_list()
        
        result = "# Kaggle Getting Started Guide\n\n"
        
        result += "## 🎯 Recommended Learning Path\n\n"
        result += "### Step 1: Start with These Competitions\n"
        
        # Find beginner-friendly competitions
        beginner_comps = [comp for comp in competitions if 'Getting Started' in getattr(comp, 'category', '')]
        for comp in beginner_comps[:5]:
            result += f"- **{comp.title}**\n"
            result += f"  - Category: {getattr(comp, 'category', 'N/A')}\n"
            result += f"  - Reward: {comp.reward}\n"
            result += f"  - URL: {comp.url}\n\n"
        
        result += "### Step 2: Practice Datasets\n"
        
        # Find small, high-quality datasets
        practice_datasets = []
        for dataset in datasets[:20]:
            if (hasattr(dataset, 'usabilityRating') and 
                dataset.usabilityRating and 
                float(dataset.usabilityRating) >= 8.0):
                practice_datasets.append(dataset)
        
        for dataset in practice_datasets[:5]:
            result += f"- **{dataset.title}**\n"
            result += f"  - Reference: {dataset.ref}\n"
            result += f"  - Size: {dataset.size}\n"
            result += f"  - Usability: {dataset.usabilityRating}/10\n\n"
        
        result += "## 📚 Learning Recommendations\n\n"
        result += "### Beginner Track\n"
        result += "1. **Titanic**: Classification basics\n"
        result += "2. **House Prices**: Regression techniques\n"
        result += "3. **Digit Recognizer**: Computer vision intro\n"
        result += "4. **NLP Disaster Tweets**: Natural language processing\n\n"
        
        result += "### Intermediate Track\n"
        result += "1. **Store Sales Forecasting**: Time series analysis\n"
        result += "2. **Spaceship Titanic**: Feature engineering\n"
        result += "3. **Connect X**: Reinforcement learning\n\n"
        
        result += "## 💡 Pro Tips\n\n"
        result += "- Start with 'Getting Started' competitions for learning\n"
        result += "- Read winning solutions and public notebooks\n"
        result += "- Join Kaggle Learn for structured courses\n"
        result += "- Participate in discussions to learn from community\n"
        result += "- Focus on understanding data before complex models\n"
        
        return result

    except Exception as e:
        logger.error(f"Error getting beginner guide resource: {e}")
        return f"Error: {str(e)}"


@mcp.resource("kaggle://meta/platform-stats")
def get_platform_stats() -> str:
    """Get Kaggle platform statistics and insights."""
    try:
        api = initialize_kaggle_api()
        competitions = api.competitions_list()
        datasets = api.dataset_list()
        models = api.model_list()
        
        result = "# Kaggle Platform Statistics\n\n"
        
        # Competition statistics
        result += "## 🏆 Competition Overview\n\n"
        total_comps = len(competitions)
        result += f"- **Total Active Competitions**: {total_comps}\n"
        
        # Category breakdown
        categories = {}
        total_prize_pool = 0
        for comp in competitions:
            category = getattr(comp, 'category', 'Unknown')
            categories[category] = categories.get(category, 0) + 1
            
            # Try to extract prize money
            if hasattr(comp, 'reward') and 'Usd' in comp.reward:
                try:
                    prize_str = comp.reward.replace('$', '').replace(',', '').replace(' Usd', '')
                    if prize_str.isdigit():
                        total_prize_pool += int(prize_str)
                except:
                    pass
        
        result += f"- **Total Prize Pool**: ${total_prize_pool:,}\n"
        result += f"- **Categories**: {len(categories)}\n\n"
        
        for category, count in sorted(categories.items(), key=lambda x: x[1], reverse=True):
            result += f"  - {category}: {count} competitions\n"
        
        # Dataset statistics
        result += "\n## 📊 Dataset Overview\n\n"
        total_datasets = len(datasets)
        result += f"- **Total Popular Datasets**: {total_datasets}\n"
        
        total_downloads = sum(getattr(dataset, 'downloadCount', 0) for dataset in datasets if hasattr(dataset, 'downloadCount'))
        result += f"- **Total Downloads**: {total_downloads:,}\n"
        
        avg_usability = sum(float(getattr(dataset, 'usabilityRating', 0)) for dataset in datasets if hasattr(dataset, 'usabilityRating') and dataset.usabilityRating) / len([d for d in datasets if hasattr(d, 'usabilityRating') and d.usabilityRating])
        result += f"- **Average Usability Rating**: {avg_usability:.1f}/10\n"
        
        # Model statistics
        result += "\n## 🤖 Model Hub Overview\n\n"
        total_models = len(models)
        result += f"- **Total Available Models**: {total_models}\n"
        
        # License distribution
        result += "\n## 📄 License Distribution\n\n"
        licenses = {}
        for dataset in datasets:
            license_name = getattr(dataset, 'licenseName', 'Unknown')
            licenses[license_name] = licenses.get(license_name, 0) + 1
        
        for license_name, count in sorted(licenses.items(), key=lambda x: x[1], reverse=True)[:5]:
            result += f"- **{license_name}**: {count} datasets\n"
        
        result += "\n## 📈 Platform Insights\n\n"
        result += f"- **Most Popular Category**: {max(categories.items(), key=lambda x: x[1])[0]}\n"
        result += f"- **Average Competitions per Category**: {total_comps / len(categories):.1f}\n"
        result += f"- **High-Value Competitions**: {len([c for c in competitions if 'Usd' in c.reward and c.reward != 'Knowledge'])}\n"
        
        return result

    except Exception as e:
        logger.error(f"Error getting platform stats resource: {e}")
        return f"Error: {str(e)}"


if __name__ == "__main__":
    # Run the MCP server
    mcp.run()
