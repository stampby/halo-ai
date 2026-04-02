#!/bin/bash
# halo-ai — Release Manager
# Tags RC or stable releases. CI handles the rest.
# Designed and built by the architect
set -euo pipefail

RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'; NC='\033[0m'

usage() {
    echo "halo-ai Release Manager"
    echo ""
    echo "Usage:"
    echo "  $0 rc <version>      Tag a release candidate (e.g., $0 rc 0.10.0)"
    echo "  $0 stable <version>  Promote to stable release (e.g., $0 stable 0.10.0)"
    echo "  $0 status            Show current version and tags"
    echo ""
    echo "Examples:"
    echo "  $0 rc 0.10.0         → tags v0.10.0-rc1 (or rc2, rc3...)"
    echo "  $0 stable 0.10.0     → tags v0.10.0 (stable, production-ready)"
}

case "${1:-help}" in
    rc)
        VERSION="${2:?Usage: $0 rc <version>}"

        # Find next RC number
        RC_NUM=1
        while git tag -l "v${VERSION}-rc${RC_NUM}" | grep -q .; do
            RC_NUM=$((RC_NUM + 1))
        done

        TAG="v${VERSION}-rc${RC_NUM}"
        echo -e "${YELLOW}Tagging release candidate: ${TAG}${NC}"
        echo -e "${YELLOW}This is for TESTING ONLY — not production.${NC}"
        echo ""
        read -p "Proceed? [y/N] " -n 1 -r
        echo ""
        [[ $REPLY =~ ^[Yy]$ ]] || exit 0

        # Run dry-run first
        echo -e "${GREEN}Running dry-run before tagging...${NC}"
        bash -n install.sh || { echo -e "${RED}Syntax check failed${NC}"; exit 1; }

        git tag -a "$TAG" -m "Release candidate ${TAG} — for testing, not production"
        git push origin "$TAG"

        echo ""
        echo -e "${GREEN}Tagged: ${TAG}${NC}"
        echo -e "CI will build and publish the RC on GitHub Releases."
        echo -e "Community can test: git checkout ${TAG}"
        ;;

    stable)
        VERSION="${2:?Usage: $0 stable <version>}"
        TAG="v${VERSION}"

        # Check that at least one RC exists
        RC_COUNT=$(git tag -l "v${VERSION}-rc*" | wc -l)
        if [ "$RC_COUNT" -eq 0 ]; then
            echo -e "${RED}No release candidates found for v${VERSION}.${NC}"
            echo -e "Run '$0 rc ${VERSION}' first and let the community test it."
            exit 1
        fi

        echo -e "${GREEN}Promoting to stable: ${TAG}${NC}"
        echo -e "RC tags found: ${RC_COUNT}"
        echo -e "${YELLOW}This will be marked as PRODUCTION-READY.${NC}"
        echo ""
        read -p "Proceed? [y/N] " -n 1 -r
        echo ""
        [[ $REPLY =~ ^[Yy]$ ]] || exit 0

        git tag -a "$TAG" -m "Stable release ${TAG} — production-ready, tested via RC"
        git push origin "$TAG"

        echo ""
        echo -e "${GREEN}Stable release: ${TAG}${NC}"
        echo -e "CI will build and publish on GitHub Releases."
        echo -e "Safe to deploy: git checkout ${TAG}"
        ;;

    status)
        echo "Current tags:"
        git tag -l "v*" --sort=-v:refname | head -10
        echo ""
        echo "Latest commit: $(git log --oneline -1)"
        ;;

    *)
        usage
        ;;
esac
