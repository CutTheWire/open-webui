#!/bin/bash
# Remove the duplicate Character Chat button under Search button

file="src/lib/components/layout/Sidebar.svelte"

# We know the duplicate button might be near line 1110-1135
# We can search for where it might have been added directly as HTML 

if grep -q "href=\"/character-chat\"" "$file" || grep -q "href='/character-chat'" "$file"; then
    echo "Found direct link"
else
    echo "No direct links found."
fi

# The issue reported was "I didn't mean to delete character chat, I meant that there are two character chat buttons in the sidebar, so remove the one right below the search button"

# Let's see if there is another place where Character Chat is rendered directly.
# Look for <button or <a> with "Character Chat" that isn't part of the pinnedItems loop
