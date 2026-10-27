# qsum

An extractive digest of long text (logs, command output) through a local OpenAI-compatible chat endpoint such as
llama.cpp or vLLM. The model is instructed to copy the important lines verbatim and never interpret; qsum then checks
that every quoted line really occurs in the input and warns about any that do not. It exists to keep large outputs out
of an expensive context window. qsum is only a client: it contains no model and trains nothing. Standard library only.

## Install

    cp qsum ~/.local/bin/ && chmod +x ~/.local/bin/qsum

## Configure

- `QSUM_ENDPOINT`: first endpoint to try. `QSUM_FALLBACKS`: comma separated list tried next (default `http://127.0.0.1:8080`). Each is probed at `/v1/models` for 3 s.
- `QSUM_MODEL`: model id (default: first id the endpoint lists). `QSUM_KEY`: optional bearer token.
- `QSUM_VERIFY_LOG`: mismatch log (default `~/.cache/qsum/verify.log`).
- Flags: `--focus "text"`, `--verify` (always check; otherwise a random 20% of runs), `--chunk N` (characters per request, default 9000).

## Example

    make test 2>&1 | qsum --focus "failing tests" --verify

## License

Apache-2.0, see `LICENSE` and `NOTICE`. Run the tests with `python3 -m pytest`.
