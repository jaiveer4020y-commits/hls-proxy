import asyncio
import json
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright


async def extract_multimovies(url):
    result = {
        "status": "error",
        "servers": [],
        "debug": []
    }

    async with async_playwright() as p:

        browser = await p.chromium.launch(
            headless=True
        )

        context = await browser.new_context(
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/128.0.0.0 Safari/537.36"
            )
        )

        page = await context.new_page()

        try:

            # ==========================================
            # OPEN PAGE
            # ==========================================

            await page.goto(
                url,
                wait_until="networkidle",
                timeout=60000
            )

            result["debug"].append({
                "step": "open_page",
                "status": "success"
            })

            html = await page.content()

            # ==========================================
            # CHECK CLOUDFLARE
            # ==========================================

            lower_html = html.lower()

            if any(x in lower_html for x in [
                "checking your browser",
                "cf-browser-verification",
                "cloudflare",
                "attention required"
            ]):
                result["error"] = (
                    "Cloudflare/interstitial detected. "
                    "Manual browser verification may be required."
                )

                await browser.close()
                return result

            # ==========================================
            # PARSE HTML
            # ==========================================

            soup = BeautifulSoup(html, "html.parser")

            # Try multiple selectors
            selectors = [
                "#player-option-1",
                "[data-post]",
                ".dooplay_player_option",
                ".player-option",
                "[data-type][data-post][data-nume]"
            ]

            player = None

            for sel in selectors:
                player = soup.select_one(sel)

                if player:
                    result["debug"].append({
                        "step": "selector_found",
                        "selector": sel
                    })
                    break

            if not player:
                result["error"] = "Player element not found."
                await browser.close()
                return result

            post_id = player.get("data-post")
            data_type = player.get("data-type")
            data_nume = player.get("data-nume")

            result["debug"].append({
                "step": "extract_attrs",
                "post": post_id,
                "type": data_type,
                "nume": data_nume
            })

            if not all([post_id, data_type, data_nume]):
                result["error"] = "Missing player attributes."
                await browser.close()
                return result

            # ==========================================
            # AJAX REQUEST INSIDE BROWSER CONTEXT
            # ==========================================

            ajax_url = url.split("/movie/")[0] + "/wp-admin/admin-ajax.php"

            payload = {
                "action": "doo_player_ajax",
                "post": post_id,
                "nume": data_nume,
                "type": data_type
            }

            response_json = await page.evaluate(
                """
                async ({ ajax_url, payload }) => {

                    const formData = new FormData();

                    for (const k in payload) {
                        formData.append(k, payload[k]);
                    }

                    const res = await fetch(ajax_url, {
                        method: "POST",
                        body: formData,
                        credentials: "include",
                        headers: {
                            "X-Requested-With": "XMLHttpRequest"
                        }
                    });

                    return await res.json();
                }
                """,
                {
                    "ajax_url": ajax_url,
                    "payload": payload
                }
            )

            result["debug"].append({
                "step": "ajax_response",
                "response": response_json
            })

            embed_url = response_json.get("embed_url")

            if not embed_url:
                result["error"] = "embed_url missing."
                await browser.close()
                return result

            result["status"] = "success"
            result["servers"] = [{
                "embed_url": embed_url,
                "type": response_json.get("type")
            }]

            await browser.close()
            return result

        except Exception as e:

            result["error"] = str(e)

            try:
                await browser.close()
            except:
                pass

            return result


# ==========================================
# RUN
# ==========================================

if __name__ == "__main__":

    url = "https://multimovies.fyi/movie/dhurandhar"

    data = asyncio.run(extract_multimovies(url))

    print(json.dumps(data, indent=2))
