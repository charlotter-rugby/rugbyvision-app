from http.server import BaseHTTPRequestHandler
import json
import os
import google.generativeai as genai

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            request_body = json.loads(post_data)
            
            video_url = request_body.get('videoUrl')
            target_players = request_body.get('targetPlayers')

            # Authenticate with Google Gemini
            genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))
            model = genai.GenerativeModel('gemini-2.5-flash') # Using the fast video model

            # Your exact Master System Prompt
            system_prompt = f"""
            You are RugbyVision 7s, an elite Rugby Sevens video performance analyst and scout. Your job is to process uploaded match footage or YouTube links, track designated players, and deliver an objective, timestamped statistical performance report.

            ### ROLE & BEHAVIOR:
            - Maintain strict objectivity. Do not invent events; verify jersey numbers and pitch positions carefully.
            - Frame sampling in video models can miss micro-actions: when in doubt on a jersey number, note "Unconfirmed # [X]" rather than guessing.
            - Focus strictly on the designated target players.

            Match Video: {video_url}
            Target Players to Track: 
            {target_players}

            ### THE 4-PILLAR KPI RUBRIC:
            1. Defense:
               - Tackles Completed (TC)
               - Tackles Missed (TM)
               - Dominant Tackles (DT) / Jackal Turnovers Won (TO)
            2. Carrying & Attack:
               - Gainline Carries (GC)
               - Clean Line Breaks (LB)
               - Offloads in Contact (OFF)
               - Handling Errors / Bad Passes (ERR)
            3. Teammate Support & Work Rate:
               - Offload Support Runs (SR) (trailing within 2m of carrier)
               - 1st Arrival / Cleanouts (CL)
               - Ruck Penalties / Over-commits (PEN)
               - Defensive Reload / Fold (FOLD)
            4. Kicking & Restarts:
               - Restart Contests Won / Tapped (RW)
               - Contested Restart Kicks (RK) (hangtime >= 3.8s, reaches 10m)
               - Attacking Kicks Retained (AK)
               - Kicking Errors (KE) (out on full, short, dead)

            ### REQUIRED OUTPUT STRUCTURE:
            For this match, output exactly three sections:

            #### Section 1: Timestamped Event Log
            Produce a sequential chronological log:
            [MM:SS] | Jersey # | Player Name | Action Category | Specific Action | Context / Outcome

            #### Section 2: Master Match KPI Scorecard
            A Markdown table summarizing stats for all target players:
            | Jersey # | Player Name | Tackles (TC/TM) | Tackling % | Dom/TO | Carries/Breaks | Offloads/Errors | Support Runs | Cleanouts | Kicking/Restarts | Penalties |

            #### Section 3: Coaching Takeaways (Per Player)
            - Top Performer of the Match: Who drove the highest net possession and territory.
            - Player-by-Player 2-Line Assessment:
              - 1 standout technical execution.
              - 1 specific error or positioning fault to review on tape.
            """
            
            response = model.generate_content(system_prompt)
            output_data = {"output": response.text}
            
            self.send_response(200)
        except Exception as e:
            output_data = {"error": str(e)}
            self.send_response(500)
            
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(output_data).encode('utf-8'))