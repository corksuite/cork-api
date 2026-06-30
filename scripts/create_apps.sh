#!/bin/bash

create_apps() {
    domain=$1
    shift

    for app in "$@"; do
        mkdir -p "apps/$domain/$app"
        python manage.py startapp "$app" "apps/$domain/$app"
    done
}

create_apps work \
    projects tasks workflows scheduling goals

create_apps collaboration \
    messages channels meetings notifications presence activity

create_apps knowledge \
    documents media wiki search

create_apps intelligence \
    ai automation analytics