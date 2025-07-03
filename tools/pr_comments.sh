#!/bin/bash

# Function to get all unresolved comment IDs for a PR
get_unresolved_comments() {
    local repo="$1"
    local pr_number="$2"
    
    # Get all review comments
    gh api repos/$repo/pulls/$pr_number/comments --paginate --jq '.[] | .id'
}

# Function to resolve a comment
resolve_comment() {
    local repo="$1"
    local pr_number="$2"
    local comment_id="$3"
    
    # GitHub doesn't have a direct API to "resolve" comments
    # But we can use GraphQL to mark review threads as resolved
    
    # First, we need to get the thread ID for the comment
    local query='query($owner: String!, $repo: String!, $pr: Int!) {
        repository(owner: $owner, name: $repo) {
            pullRequest(number: $pr) {
                reviewThreads(first: 100) {
                    nodes {
                        id
                        isResolved
                        comments(first: 100) {
                            nodes {
                                databaseId
                            }
                        }
                    }
                }
            }
        }
    }'
    
    local owner=$(echo $repo | cut -d'/' -f1)
    local repo_name=$(echo $repo | cut -d'/' -f2)
    
    # Find the thread ID that contains our comment
    local thread_data=$(gh api graphql -f query="$query" -f owner="$owner" -f repo="$repo_name" -F pr="$pr_number")
    
    # Extract thread ID for the comment
    local thread_id=$(echo "$thread_data" | jq -r --arg comment_id "$comment_id" '
        .data.repository.pullRequest.reviewThreads.nodes[] |
        select(.comments.nodes[].databaseId == ($comment_id | tonumber)) |
        select(.isResolved == false) |
        .id
    ')
    
    if [ -n "$thread_id" ]; then
        # Resolve the thread
        local mutation='mutation($threadId: ID!) {
            resolveReviewThread(input: {threadId: $threadId}) {
                thread {
                    isResolved
                }
            }
        }'
        
        gh api graphql -f query="$mutation" -f threadId="$thread_id"
        echo "Resolved thread for comment $comment_id"
    else
        echo "No unresolved thread found for comment $comment_id"
    fi
}

# Function to get only unresolved comments with details
get_unresolved_comments_detailed() {
    local repo="$1"
    local pr_number="$2"
    
    local owner=$(echo $repo | cut -d'/' -f1)
    local repo_name=$(echo $repo | cut -d'/' -f2)
    
    local query='query($owner: String!, $repo: String!, $pr: Int!) {
        repository(owner: $owner, name: $repo) {
            pullRequest(number: $pr) {
                reviewThreads(first: 100) {
                    nodes {
                        id
                        isResolved
                        path
                        line
                        comments(first: 100) {
                            nodes {
                                databaseId
                                author {
                                    login
                                }
                                body
                            }
                        }
                    }
                }
            }
        }
    }'
    
    gh api graphql -f query="$query" -f owner="$owner" -f repo="$repo_name" -F pr="$pr_number" | \
    jq -r '.data.repository.pullRequest.reviewThreads.nodes[] | 
        select(.isResolved == false) | 
        .comments.nodes[] | 
        "\(.databaseId)\t\(.author.login)\t\(.body | split("\n")[0] | .[0:80])"'
}

# Function to resolve all unresolved comments
resolve_all_comments() {
    local repo="$1"
    local pr_number="$2"
    
    echo "Finding unresolved comments..."
    
    local owner=$(echo $repo | cut -d'/' -f1)
    local repo_name=$(echo $repo | cut -d'/' -f2)
    
    # Get unresolved thread IDs directly
    local query='query($owner: String!, $repo: String!, $pr: Int!) {
        repository(owner: $owner, name: $repo) {
            pullRequest(number: $pr) {
                reviewThreads(first: 100) {
                    nodes {
                        id
                        isResolved
                    }
                }
            }
        }
    }'
    
    local thread_ids=$(gh api graphql -f query="$query" -f owner="$owner" -f repo="$repo_name" -F pr="$pr_number" | \
        jq -r '.data.repository.pullRequest.reviewThreads.nodes[] | select(.isResolved == false) | .id')
    
    # Resolve each thread
    local mutation='mutation($threadId: ID!) {
        resolveReviewThread(input: {threadId: $threadId}) {
            thread {
                isResolved
            }
        }
    }'
    
    while IFS= read -r thread_id; do
        if [ -n "$thread_id" ]; then
            echo "Resolving thread: $thread_id"
            gh api graphql -f query="$mutation" -f threadId="$thread_id"
            sleep 0.5  # Rate limiting
        fi
    done <<< "$thread_ids"
    
    echo "Done!"
}

# Usage
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    echo "Usage: source this file and then run:"
    echo "  get_unresolved_comments_detailed 'owner/repo' PR_NUMBER    # List unresolved comments"
    echo "  resolve_all_comments 'owner/repo' PR_NUMBER                # Resolve all unresolved comments"
    echo "  resolve_comment 'owner/repo' PR_NUMBER COMMENT_ID          # Resolve specific comment"
    echo ""
    echo "Example:"
    echo "  get_unresolved_comments_detailed 'owner/repo' 2"
    echo "  resolve_all_comments 'owner/repo' 2"
fi
# Function to get just the IDs of unresolved comments
get_unresolved_comment_ids() {
    local repo="$1"
    local pr_number="$2"
    
    local owner=$(echo $repo | cut -d'/' -f1)
    local repo_name=$(echo $repo | cut -d'/' -f2)
    
    local query='query($owner: String!, $repo: String!, $pr: Int!) {
        repository(owner: $owner, name: $repo) {
            pullRequest(number: $pr) {
                reviewThreads(first: 100) {
                    nodes {
                        isResolved
                        comments(first: 100) {
                            nodes {
                                databaseId
                            }
                        }
                    }
                }
            }
        }
    }'
    
    gh api graphql -f query="$query" -f owner="$owner" -f repo="$repo_name" -F pr="$pr_number" | \
    jq -r '.data.repository.pullRequest.reviewThreads.nodes[] | 
        select(.isResolved == false) | 
        .comments.nodes[].databaseId'
}