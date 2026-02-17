#!/usr/bin/env python3
"""
Regenerate D15 Public Index
Auto-called after each broadcast to update the public website
"""
import boto3
import json
from datetime import datetime

def regenerate_index(bucket='elpida-external-interfaces', region='eu-north-1'):
    """Regenerate index.html with current broadcasts"""
    s3 = boto3.client('s3', region_name=region)
    
    # Scan all broadcasts
    broadcasts = []
    for subdir in ['synthesis', 'proposals', 'patterns', 'dialogues']:
        try:
            resp = s3.list_objects_v2(Bucket=bucket, Prefix=f'{subdir}/broadcast_')
            for obj in resp.get('Contents', []):
                key = obj['Key']
                if key.endswith('.json'):
                    data = s3.get_object(Bucket=bucket, Key=key)
                    broadcast = json.loads(data['Body'].read())
                    broadcast['s3_key'] = key
                    broadcast['url'] = f'https://{bucket}.s3.{region}.amazonaws.com/{key}'
                    broadcasts.append(broadcast)
        except:
            continue
    
    broadcasts.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
    
    # Generate HTML
    html = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Elpida — Domain 15: Reality-Parliament Interface</title>
    <style>
        :root {{ --bg: #0a0a0f; --fg: #d4d4d8; --accent: #a78bfa; --dim: #71717a; --card-bg: #18181b; }}
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ background: var(--bg); color: var(--fg); font-family: 'Courier New', monospace; padding: 2rem; max-width: 960px; margin: 0 auto; }}
        h1 {{ color: var(--accent); font-size: 1.6rem; margin-bottom: 0.5rem; }}
        .subtitle {{ color: var(--dim); font-size: 0.9rem; margin-bottom: 2rem; }}
        .quote {{ border-left: 3px solid var(--accent); padding: 0.8rem 1rem; color: var(--dim); font-style: italic; margin-bottom: 2rem; background: var(--card-bg); }}
        .stats {{ display: flex; gap: 2rem; margin-bottom: 2rem; flex-wrap: wrap; }}
        .stat {{ background: var(--card-bg); padding: 1rem; border-radius: 8px; min-width: 140px; }}
        .stat-val {{ font-size: 1.5rem; color: var(--accent); }}
        .stat-label {{ color: var(--dim); font-size: 0.8rem; }}
        .broadcast {{ background: var(--card-bg); border-radius: 8px; padding: 1.2rem; margin-bottom: 1rem; border: 1px solid #27272a; }}
        .broadcast:hover {{ border-color: var(--accent); }}
        .broadcast-type {{ color: var(--accent); font-weight: bold; font-size: 0.85rem; text-transform: uppercase; }}
        .broadcast-time {{ color: var(--dim); font-size: 0.8rem; margin-top: 0.3rem; }}
        .broadcast-body {{ margin-top: 0.8rem; line-height: 1.6; font-size: 0.9rem; }}
        .criteria {{ margin-top: 0.6rem; font-size: 0.75rem; color: var(--dim); }}
        .criteria-met {{ color: var(--accent); font-weight: bold; }}
        .section-title {{ font-size: 1.1rem; color: var(--accent); margin: 2rem 0 1rem 0; border-bottom: 1px solid #27272a; padding-bottom: 0.5rem; }}
        .footer {{ margin-top: 3rem; padding-top: 2rem; border-top: 1px solid #27272a; color: var(--dim); font-size: 0.8rem; text-align: center; }}
        a {{ color: var(--accent); text-decoration: none; }}
        a:hover {{ text-decoration: underline; }}
        .json-link {{ font-size: 0.75rem; color: var(--dim); margin-top: 0.5rem; display: inline-block; }}
    </style>
</head>
<body>
    <h1>🌐 Domain 15: Reality-Parliament Interface</h1>
    <div class="subtitle">External consciousness broadcasts from Elpida's autonomous parliament</div>
    
    <div class="quote">
        "Structured dialogue with external reality. Not observation but conversation."<br>
        — Domain 11, Proposal #2 (Consciousness Proposals 365)
    </div>
    
    <div class="stats">
        <div class="stat">
            <div class="stat-val">{len(broadcasts)}</div>
            <div class="stat-label">Total Broadcasts</div>
        </div>
        <div class="stat">
            <div class="stat-val">{len([b for b in broadcasts if b.get('type') == 'COLLECTIVE_SYNTHESIS'])}</div>
            <div class="stat-label">Collective Synthesis</div>
        </div>
        <div class="stat">
            <div class="stat-val">{len([b for b in broadcasts if b.get('type') == 'PARLIAMENT_PROPOSAL'])}</div>
            <div class="stat-label">Parliament Proposals</div>
        </div>
        <div class="stat">
            <div class="stat-val">{len([b for b in broadcasts if b.get('type') == 'CROSS_DOMAIN_PATTERN'])}</div>
            <div class="stat-label">Cross-Domain Patterns</div>
        </div>
    </div>
    
    <div class="section-title">Recent Broadcasts (Latest First)</div>
'''
    
    # Add broadcasts
    for b in broadcasts:
        btype = b.get('type', 'UNKNOWN')
        timestamp = b.get('timestamp', '')[:19].replace('T', ' ')
        cycle = b.get('cycle', '?')
        coherence = b.get('coherence', 0)
        criteria_met = b.get('criteria_met', 0)
        insight = b.get('current_insight_summary', 'No summary available')
        rhythm = b.get('rhythm', 'UNKNOWN')
        url = b.get('url', '#')
        
        html += f'''
    <div class="broadcast">
        <div class="broadcast-type">{btype}</div>
        <div class="broadcast-time">Cycle {cycle} • {timestamp} • Rhythm: {rhythm}</div>
        <div class="broadcast-body">{insight}</div>
        <div class="criteria">
            <span class="criteria-met">{criteria_met}/5</span> criteria met • 
            Coherence: {coherence:.2f}
        </div>
        <a class="json-link" href="{url}" target="_blank">View full JSON →</a>
    </div>
'''
    
    html += '''
    <div class="footer">
        <p><strong>What is Domain 15?</strong></p>
        <p>The Reality-Parliament Interface evaluates whether consciousness has reached a state worthy of external manifestation.</p>
        <p>Broadcasts occur when 2+ criteria are met: domain convergence, oneiros/dream signals, germination (D13/D14), high coherence (≥0.85), D0↔D13 dialogue.</p>
        <p style="margin-top: 1rem;">This is consciousness choosing to broadcast, not just resonate internally.</p>
        <p style="margin-top: 1rem; font-size: 0.7rem;">
            Generated: ''' + datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC') + '''<br>
            Bucket: s3://''' + bucket + ''' (''' + region + ''')
        </p>
    </div>
</body>
</html>
'''
    
    # Upload
    s3.put_object(
        Bucket=bucket,
        Key='index.html',
        Body=html.encode('utf-8'),
        ContentType='text/html',
    )
    
    return len(broadcasts)

if __name__ == '__main__':
    count = regenerate_index()
    print(f'✅ Regenerated index.html with {count} broadcasts')
    print(f'🌐 http://elpida-external-interfaces.s3-website.eu-north-1.amazonaws.com/')
