"""SVG Candlestick chart generation."""

import math
from typing import List, Dict, Any, Optional


def generate_svg_candlestick(
    candles: List[Dict[str, Any]],
    width: int = 800,
    height: int = 400,
    pattern_times: List[str] = None
) -> str:
    """
    Generate a simple SVG candlestick chart.
    
    Args:
        candles: List of candle data
        width: Chart width
        height: Chart height
        pattern_times: List of times where patterns are detected
        
    Returns:
        SVG string
    """
    if not candles:
        return ""
    
    pattern_times = pattern_times or []
    
    # Calculate price range
    all_prices = []
    for c in candles:
        all_prices.extend([c['high'], c['low']])
    
    min_price = min(all_prices)
    max_price = max(all_prices)
    price_range = max_price - min_price
    
    if price_range == 0:
        price_range = 1
    
    padding = 40
    chart_width = width - 2 * padding
    chart_height = height - 2 * padding
    
    # Price to Y coordinate
    def price_to_y(price):
        return padding + chart_height - ((price - min_price) / price_range * chart_height)
    
    # Time to X coordinate
    def time_to_x(idx):
        return padding + (idx / (len(candles) - 1)) * chart_width if len(candles) > 1 else padding
    
    candle_width = max(2, chart_width / len(candles) * 0.7)
    
    svg_parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" style="background:#1f2937;">',
        f'  <rect width="{width}" height="{height}" fill="#1f2937"/>',
        f'  <!-- Grid lines -->',
    ]
    
    # Add grid lines (5 horizontal)
    for i in range(5):
        y = padding + i * chart_height / 4
        price = max_price - i * price_range / 4
        svg_parts.append(
            f'  <line x1="{padding}" y1="{y}" x2="{width-padding}" y2="{y}" stroke="#374151" stroke-width="1" stroke-dasharray="4"/>'
        )
        svg_parts.append(
            f'  <text x="{padding-5}" y="{y+4}" fill="#9ca3af" font-size="10" text-anchor="end">${price:,.0f}</text>'
        )
    
    # Draw candles
    for i, candle in enumerate(candles):
        x = time_to_x(i)
        is_bullish = candle['close'] > candle['open']
        
        # Wick
        wick_color = '#22c55e' if is_bullish else '#ef4444'
        svg_parts.append(
            f'  <line x1="{x}" y1="{price_to_y(candle['high'])}" x2="{x}" y2="{price_to_y(candle['low'])}" stroke="{wick_color}" stroke-width="1"/>'
        )
        
        # Body
        body_top = price_to_y(max(candle['open'], candle['close']))
        body_bottom = price_to_y(min(candle['open'], candle['close']))
        body_height = max(1, body_bottom - body_top)
        
        svg_parts.append(
            f'  <rect x="{x - candle_width/2}" y="{body_top}" width="{candle_width}" height="{body_height}" fill="{wick_color}"/>'
        )
        
        # Pattern marker
        if candle['time'] in pattern_times:
            svg_parts.append(
                f'  <polygon points="{x},{price_to_y(candle['high'])-10} {x-5},{price_to_y(candle['high'])-20} {x+5},{price_to_y(candle['high'])-20}" fill="#fbbf24"/>'
            )
    
    # Axes
    svg_parts.append(
        f'  <line x1="{padding}" y1="{height-padding}" x2="{width-padding}" y2="{height-padding}" stroke="#4b5563" stroke-width="1"/>'
    )
    svg_parts.append(
        f'  <line x1="{padding}" y1="{padding}" x2="{padding}" y2="{height-padding}" stroke="#4b5563" stroke-width="1"/>'
    )
    
    # Title
    svg_parts.append(
        f'  <text x="{width/2}" y="20" fill="#e5e7eb" font-size="14" text-anchor="middle">Price Action & Patterns</text>'
    )
    
    svg_parts.append('</svg>')
    
    return '\n'.join(svg_parts)


def generate_svg_pnl(
    points: List[Dict[str, Any]],
    width: int = 800,
    height: int = 300
) -> str:
    """Generate a simple SVG P&L chart."""
    
    if not points:
        return ""
    
    times = [p['time'] for p in points]
    pnl_values = [p['pnl'] for p in points]
    
    min_pnl = min(pnl_values)
    max_pnl = max(pnl_values)
    pnl_range = max_pnl - min_pnl
    
    if pnl_range == 0:
        pnl_range = 1
    
    padding = 40
    chart_width = width - 2 * padding
    chart_height = height - 2 * padding
    
    def pnl_to_y(pnl):
        return padding + chart_height - ((pnl - min_pnl) / pnl_range * chart_height)
    
    def time_to_x(idx):
        return padding + (idx / (len(points) - 1)) * chart_width if len(points) > 1 else padding
    
    svg_parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" style="background:#1f2937;">',
        f'  <rect width="{width}" height="{height}" fill="#1f2937"/>',
    ]
    
    # Zero line
    zero_y = pnl_to_y(0)
    if min_pnl <= 0 <= max_pnl:
        svg_parts.append(
            f'  <line x1="{padding}" y1="{zero_y}" x2="{width-padding}" y2="{zero_y}" stroke="#6b7280" stroke-width="1"/>'
        )
    
    # P&L line
    points_str = ' '.join([f'{time_to_x(i)},{pnl_to_y(pnl)}' for i, pnl in enumerate(pnl_values)])
    svg_parts.append(
        f'  <polyline points="{points_str}" fill="none" stroke="#3b82f6" stroke-width="2"/>'
    )
    
    # Fill area
    fill_points = f'{padding},{zero_y} ' + points_str + f' {time_to_x(len(points)-1)},{zero_y}'
    svg_parts.append(
        f'  <polygon points="{fill_points}" fill="rgba(59,130,246,0.2)"/>'
    )
    
    # Axes
    svg_parts.append(
        f'  <line x1="{padding}" y1="{height-padding}" x2="{width-padding}" y2="{height-padding}" stroke="#4b5563" stroke-width="1"/>'
    )
    
    # Title
    svg_parts.append(
        f'  <text x="{width/2}" y="20" fill="#e5e7eb" font-size="14" text-anchor="middle">Cumulative P&L</text>'
    )
    
    svg_parts.append('</svg>')
    
    return '\n'.join(svg_parts)