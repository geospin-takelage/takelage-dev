#!/usr/bin/env bash

# bash color escape sequences
color_red=$'\001'$(tput setaf 1 2>/dev/null || echo $'\e[31m')$'\002'
color_green=$'\001'$(tput setaf 2 2>/dev/null || echo $'\e[32m')$'\002'
color_blue=$'\001'$(tput setaf 4 2>/dev/null || echo $'\e[34m')$'\002'
color_reset=$'\001'$(tput sgr 0 2>/dev/null || echo $'\e[0m')$'\002'
prompt_orange='\[\e[1;38;5;214m\]'
prompt_white='\[\e[37;1m\]'
prompt_reset='\[\e[0m\]'

# dereference git symbolic reference HEAD to get branch name or sha1 of commit
# object and amend by information about current status of staging area
dereference_git_HEAD() {
    local sha1=$(git rev-parse --short HEAD 2>&1)
    if [ $? -eq 0 ]; then
        local color_symref=$color_green
        local color_ref=$color_blue
        local dirty=$(git status --porcelain 2>&1)
        if [ ! -z "$dirty" ]; then
            color_symref=$color_red
            color_ref=$color_red
            dirty='*'
        fi
        GIT_HEAD_PROMPT="$color_symref-($(git symbolic-ref --quiet --short HEAD)$dirty)$color_reset"
        if [ $? -ne 0 ]; then
            GIT_HEAD_PROMPT="$color_ref-[$sha1$dirty]$color_reset"
        fi
        GIT_HEAD_PROMPT=$GIT_HEAD_PROMPT
    else
        GIT_HEAD_PROMPT=""
    fi
}

# determine exit status of last command
exit_status() {
  local exit_status="$?"
  if [ $exit_status != 0 ]; then
    EXIT_STATUS="$color_red($exit_status)-$color_reset"
  else
    EXIT_STATUS="$color_green($exit_status)-$color_reset"
  fi

}

# run command before bash takes PS1 to build prompt
PROMPT_COMMAND="exit_status; dereference_git_HEAD; $PROMPT_COMMAND"

# fancy prompt
export PS1="\n${prompt_orange}\$EXIT_STATUS${prompt_orange}(${prompt_white}\u${prompt_orange})-(${prompt_white}${HOSTNAME#*_}${prompt_orange})-(${prompt_white}\w${prompt_orange})\$GIT_HEAD_PROMPT\n${prompt_orange}(\[${prompt_white}#\!${prompt_orange})-(\[${prompt_white}\t${prompt_orange})${prompt_reset} "'\$ '