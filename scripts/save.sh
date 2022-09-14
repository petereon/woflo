#!/bin/bash

function usage() {
  echo "Usage: "
  echo "  ./scripts/save.sh chore                              # chore: <message>"
  echo "  ./scripts/save.sh desc                               # docs: description added"
  echo "  ./scripts/save.sh (p | plan | plans)                 # docs: user stories added"
  echo "  ./scripts/save.sh (td | techdebt)                    # docs: updated techdebt"
  echo "  ./scripts/save.sh (n | note | notes)                 # docs: updated notes"
  echo "  ./scripts/save.sh uat <us> <uat> (r | red)           # feat(us<us>/uat<uat>): red"
  echo "  ./scripts/save.sh uat <us> <uat> (g | green)         # feat(us<us>/uat<uat>): green"
  echo "  ./scripts/save.sh uat <us> <uat> ref <message>       # refactor(us<us>/uat<uat>): <message>"
  echo "  ./scripts/save.sh uat <us> <uat> (c | covered)       # test(us<us>/uat<uat>): added already covered test case"
  echo "  ./scripts/save.sh uat <us> <uat> (d | done)          # feat(us<us>/uat<uat>): done"
  echo "  ./scripts/save.sh us <us> done                       # feat(us<us>): done"
  exit 1
}

function checkNotEmpty() {
  if [[ -z "$1" ]]; then
    usage
    exit 1
  fi
}

function uatMessage() {
  TYPE="$1"
  US="$2"
  UAT="$3"
  MSG="$4"
  SCOPE="us$US/uat$US.$UAT"
  echo "$TYPE($SCOPE): $MSG"
}

function commit() {
  git add .
  git commit -m "$1" $2
  exit 0
}

ACTION="$1"

checkNotEmpty "$ACTION"

case "$ACTION" in

  "chore")
    MSG="$2"
    checkNotEmpty "$MSG"
    commit "chore: 🧹 $MSG"
    ;;

  "desc")
    commit "docs: 📝 added kata description"
    ;;

  "p" | "plan" | "plans")
    commit "docs: 📝 added user stories"
    ;;

  "td" | "techdebt")
    commit "docs: 📝 updated techdebt"
    ;;

  "n" | "note" | "notes")
    commit "docs: 📝 updated notes"
    ;;

  "uat")
    US="$2"
    UAT="$3"
    PHASE="$4"
    CUSTOM_MESSAGE="$5"
    MSG=""
    COMMIT_OPTS=""

    checkNotEmpty "$US"
    checkNotEmpty "$UAT"
    checkNotEmpty "$PHASE"

    case "$PHASE" in

      "r" | "red")
	      MSG=$(uatMessage feat "$US" "$UAT" "🔴 red")
        ;;

      "g" | "green")
        MSG=$(uatMessage feat "$US" "$UAT" "🟢 green")
        ;;

      "ref")
	      checkNotEmpty "$CUSTOM_MESSAGE"
        MSG=$(uatMessage refactor "$US" "$UAT" "👩‍💻 $CUSTOM_MESSAGE")
        ;;

      "c" | "covered")
        MSG=$(uatMessage test "$US" "$UAT" "🟢 added already covered test case")
        ;;

      "d" | "done")
        MSG=$(uatMessage feat "$US" "$UAT" "🟢 done")
        ;;

      *)
        usage
	;;
    esac

    commit "$MSG" "$COMMIT_OPTS"
    ;;

  "us")
    US="$2"
    checkNotEmpty "$US"

    commit "feat(US$US): 🟢 done"
    ;;

  *)
    usage
    ;;

esac
