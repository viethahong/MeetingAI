import click
from pathlib import Path
from .config import Settings
from .pipeline import run_pipeline

@click.command()
@click.argument("input_source")
@click.option("--language", "-l", default="Vietnamese", help="Ngôn ngữ của audio")
@click.option("--llm", default="gemini", type=click.Choice(["gemini", "ollama", "none"]), help="Backend LLM")
@click.option("--output-dir", "-o", default="./output", help="Thư mục output")
@click.option("--model", default="large-v3-turbo", help="Whisper model")
def main(input_source: str, language: str, llm: str, output_dir: str, model: str):
    config = Settings()
    config.WHISPER_LANGUAGE = language
    config.LLM_BACKEND = llm
    config.OUTPUT_DIR = Path(output_dir)
    config.WHISPER_MODEL = model
    
    click.echo(f"Processing: {input_source}")
    click.echo(f"Config: Language={language}, LLM={llm}, Output={output_dir}, Model={model}")
    
    def log_progress(msg: str, progress: float):
        click.echo(f"[{progress*100:0.0f}%] {msg}")
        
    try:
        result = run_pipeline(input_source, config, progress_callback=log_progress)
        click.echo("Hoàn thành quá trình thành công!")
        click.echo("Các file được sinh ra:")
        for file in result.output_files:
            click.echo(f" - {file}")
            
    except Exception as e:
        click.echo(f"Lỗi xảy ra: {str(e)}", err=True)
        import traceback
        click.echo(traceback.format_exc(), err=True)

if __name__ == "__main__":
    main()
