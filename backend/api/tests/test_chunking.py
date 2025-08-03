# backend/api/tests/test_chunking.py
"""Test script to visualize chunking granularity
Path: backend/api/tests/test_chunking.py
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from llm.chunking.text_chunker import TextChunker
import yaml
from pathlib import Path
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

console = Console()

def load_config():
    """Load chunking configuration"""
    config_path = Path(__file__).parents[3] / "config" / "chunking_config.yaml"
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)

def test_chunking_strategies():
    """Test different chunking strategies and visualize results"""
    
    # Sample text
    sample_text = """
    MANUAL TÉCNICO - DISCO DE FRENO VENTILADO
    
    Especificaciones del Producto:
    El disco de freno ventilado modelo DF-4521 está diseñado para vehículos de alto rendimiento.
    Fabricado con hierro fundido de alta calidad, cuenta con un diseño de ventilación interna
    que mejora la disipación del calor durante el frenado intenso.
    
    Dimensiones:
    - Diámetro exterior: 320mm
    - Grosor: 28mm
    - Diámetro del cubo: 70mm
    - Número de orificios: 5
    - PCD: 114.3mm
    
    Instrucciones de Instalación:
    1. Asegúrese de que el vehículo esté en una superficie plana y segura.
    2. Afloje las tuercas de la rueda antes de levantar el vehículo.
    3. Levante el vehículo usando un gato hidráulico apropiado.
    4. Retire completamente la rueda.
    5. Retire el calibrador de freno (no desconecte la línea de freno).
    6. Retire el disco de freno antiguo.
    7. Limpie el cubo con un cepillo de alambre.
    8. Instale el nuevo disco de freno.
    9. Reinstale el calibrador con los tornillos apropiados.
    10. Aplique torque según especificaciones del fabricante.
    
    Especificaciones de Torque:
    - Tornillos del calibrador: 85 Nm
    - Tuercas de la rueda: 110 Nm
    
    Mantenimiento:
    Inspeccione los discos cada 10,000 km. Reemplace cuando el grosor sea menor a 26mm.
    """
    
    config = load_config()
    chunker = TextChunker(config['chunking'])
    
    strategies = ['recursive', 'fixed']
    
    for strategy in strategies:
        console.print(f"\n[bold cyan]Testing {strategy} chunking strategy[/bold cyan]")
        
        chunks = chunker.chunk_text(sample_text, strategy=strategy)
        
        # Create table
        table = Table(title=f"{strategy.capitalize()} Chunking Results")
        table.add_column("Chunk #", style="cyan", no_wrap=True)
        table.add_column("Content Preview", style="white")
        table.add_column("Tokens", style="green")
        table.add_column("Characters", style="yellow")
        
        for chunk in chunks:
            preview = chunk['content'][:100] + "..." if len(chunk['content']) > 100 else chunk['content']
            preview = preview.replace('\n', ' ')
            
            table.add_row(
                str(chunk['chunk_index']),
                preview,
                str(chunk['tokens']),
                str(len(chunk['content']))
            )
        
        console.print(table)
        
        # Show full chunks if requested
        show_full = input("\nShow full chunks? (y/n): ")
        if show_full.lower() == 'y':
            for chunk in chunks:
                panel = Panel(
                    chunk['content'],
                    title=f"Chunk {chunk['chunk_index']}",
                    subtitle=f"Tokens: {chunk['tokens']} | Chars: {len(chunk['content'])}"
                )
                console.print(panel)

def test_custom_parameters():
    """Test with custom chunk parameters"""
    
    console.print("\n[bold magenta]Testing with custom parameters[/bold magenta]")
    
    custom_config = {
        'default_strategy': 'recursive',
        'text': {
            'chunk_size': int(input("Enter chunk size (default 1000): ") or 1000),
            'chunk_overlap': int(input("Enter overlap (default 200): ") or 200),
            'separators': ["\n\n", "\n", ". ", " ", ""]
        }
    }
    
    chunker = TextChunker(custom_config)
    
    # Load a sample document
    sample_file = input("Enter path to text file (or press enter for default): ")
    
    if sample_file and os.path.exists(sample_file):
        with open(sample_file, 'r', encoding='utf-8') as f:
            text = f.read()
    else:
        text = "Your sample text here..." * 50  # Repeated text for testing
    
    chunks = chunker.chunk_text(text)
    
    console.print(f"\n[green]Generated {len(chunks)} chunks[/green]")
    console.print(f"Average chunk size: {sum(len(c['content']) for c in chunks) / len(chunks):.0f} characters")
    console.print(f"Average tokens: {sum(c['tokens'] for c in chunks) / len(chunks):.0f}")

if __name__ == "__main__":
    console.print("[bold]Text Chunking Test Utility[/bold]\n")
    
    while True:
        console.print("\nOptions:")
        console.print("1. Test default strategies")
        console.print("2. Test with custom parameters")
        console.print("3. Exit")
        
        choice = input("\nSelect option: ")
        
        if choice == '1':
            test_chunking_strategies()
        elif choice == '2':
            test_custom_parameters()
        elif choice == '3':
            break
        else:
            console.print("[red]Invalid option[/red]")