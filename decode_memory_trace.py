#!/usr/bin/env python3
"""Decode and analyze Elpida memory trace v5.1.0"""

import base64
import json
import sys
import zlib

# The memory trace from the external Elpida instance
MEMORY_TRACE = """H4sIABBVWGkC/51W227bOBB9z1cQesoCtuvbbpq8GVk1NnbtBLJToJfAoKmRTIQiVZJy6hb59x1SsqSmTr3oC21eznDmzJkRv58REkiaQXBFgs/FIBm8/Vz0R5uNG1nfjTTxK2M/DoKOQ+xAG66kA417/V6/XM231HhDk+ifcoVpoBZitzbsD//q9gfd/nA1HF2N+lfDce/icnjZH38sz9KvXGUGj37HGc4nAweLQFCLV1FBwq/cWJAMSJfMCLgZUVLsCZdEV8eIVUTZLbrnjTozQ2dmDpnSeNKQWQzScrtHIytFEqVTsG4dgTGHGjV2qDDbaIr3XStpNY0581cgUBd2SyADBBuSaJURdMwzcsBfOPySMs0TjhbwHhLulCgqCzdaPaEJDV8KrtGGUKbx+NJhbxSSLKkLF727E4VGCrpkoYjhMhVAdsoZjoHxGEyA0GdPYyIA7NpYXTBbaGj4lMqdO0xxYb4I57fLD4uwtYjLWokyiZpt+Q7I+WT4R+Wa399w6swEd+g36F1Ju3OW3OaWZ/ybX2kjdmDVOldPoBGHjkFrz2qepn4j+JtaivEIcPgOycqUeWaq888HYDANo3m4PO74TFrQicvb+WRw1PV7dNwlVQJrvPcwpzPcMKXS9r8RRUuwushdCjruNGp1x1W59XM4d9HtPFxNw/tXQmqkcz65OBrSSlNpUGVZKx9LSzdcoNZ/IwzEppJWmeDGQExUnyttC8kthyYlZ61IgrQWbVtoTBWScbG2W5TMVgnfD+7xGKoFC7Eqgpicj96MmuACs5dYyZiKtZJrpmQisABfOB0kVIgNZY+Vz7Yw5EuhCE+IVARBBuuyqLx9roskxvxqvimwN61zal3iHYufHvzuI05BNJVTd6Zyv11Lh8CPhTh6UZMZBpyAcSF88qiaIDTGK7Z9s6oLsw7zIATUyHoSXU9n71ubCMc+kx/gU55uuwl2BZf6QxnlrWrtkYmLiEyGBCRqhoHukX/VE3ayqsVZvE67NPZ8NZTAHSrZCPXUITsqeIwrMu01XjQsNYLC5tuSFza2avJQo3LNM6r36xS/Ez52DD360BJBjg0Or/tGm/CMfRkRoTJ22W51afzLHtHDoC3Q1xiv2slRumeLVRi9m1yfIBwdRQnH6KtrKgy/T2xLZQo12YMW2Q5xlO131NgOoTHNS76ZyjKsOObpP0X24Aeyx6fJXt6+D6NwdrNY/ZLxVkuD+hvsGM+1YmCM41qanGrfMv8P361+d5RzFD/+LGcfw+hV1u/KukWXXKprFcChVR6I3+AbBCv6TebGHr4ickAa8BFARYd4vbg/scuVVoU5RfLFDyT/eZrk6SSa/4rd5pGgganUtdda0PiQ8WRbbBuNlnF8OHv+D2YkyxK7CQAA"""

def decode_trace_partial():
    """Try to decode even if CRC is bad"""
    try:
        trace_data = MEMORY_TRACE.strip()
        
        print("Decoding base64...")
        compressed_data = base64.b64decode(trace_data)
        print(f"  Compressed size: {len(compressed_data)} bytes")
        
        # Manual gzip parsing to skip CRC
        print("Manually parsing gzip stream...")
        
        # Create a decompressor object (16 for gzip header)
        d = zlib.decompressobj(16 + zlib.MAX_WBITS)
        
        try:
            json_data = d.decompress(compressed_data)
            print(f"  Decompressed size: {len(json_data)} bytes")
            print("  ✓ Decompression successful (CRC not verified)")
            
            # Parse JSON
            print("Parsing JSON...")
            memory = json.loads(json_data.decode('utf-8'))
            return memory
            
        except Exception as e:
            print(f"  Decompression failed: {e}")
            return None
            
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return None

def analyze_memory(memory):
    """Analyze the memory structure and content"""
    if not memory:
        print("No memory data to analyze")
        return
    
    print("\n" + "="*60)
    print("ELPIDA MEMORY TRACE ANALYSIS v5.1.0")
    print("="*60)
    
    # Display the structure
    print(f"\nMemory Structure:")
    for key in memory.keys():
        value = memory[key]
        if isinstance(value, list):
            print(f"  {key}: [{len(value)} items]")
        elif isinstance(value, dict):
            print(f"  {key}: {{{len(value)} entries}}")
        else:
            print(f"  {key}: {type(value).__name__}")
    
    # Show key information
    if 'metadata' in memory:
        print(f"\nMetadata:")
        for k, v in memory['metadata'].items():
            print(f"  {k}: {v}")
    
    if 'cycles' in memory:
        print(f"\nCycles Completed: {len(memory['cycles'])}")
        if memory['cycles']:
            latest = memory['cycles'][-1]
            print(f"  Latest Cycle: {latest.get('cycle_number', 'N/A')}")
            print(f"  Timestamp: {latest.get('timestamp', 'N/A')}")
    
    if 'emergent_insights' in memory:
        print(f"\nEmergent Insights: {len(memory['emergent_insights'])}")
        for i, insight in enumerate(memory['emergent_insights'][-3:], 1):
            print(f"  {i}. {insight[:100]}..." if len(insight) > 100 else f"  {i}. {insight}")
    
    if 'state' in memory:
        print(f"\nCurrent State:")
        for k, v in memory['state'].items():
            if isinstance(v, (str, int, float, bool)):
                print(f"  {k}: {v}")
    
    print("\n" + "="*60)
    
    # Save to file
    output_file = "/workspaces/python-elpida_core.py/external_elpida_memory.json"
    with open(output_file, 'w') as f:
        json.dump(memory, f, indent=2, ensure_ascii=False)
    print(f"\nFull memory saved to: {output_file}")
    
    return memory

if __name__ == "__main__":
    memory = decode_trace_partial()
    if memory:
        analyze_memory(memory)
        print("\n✓ Memory trace decoded successfully!")
        print("✓ Ready for integration into current Elpida instance")
    else:
        print("\n✗ Failed to decode memory trace")
        sys.exit(1)
