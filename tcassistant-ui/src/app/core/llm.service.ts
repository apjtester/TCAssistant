import { Injectable } from '@angular/core';
import { map, Observable, of, tap } from 'rxjs';
import { HttpClient } from '@angular/common/http';

@Injectable({
  providedIn: 'root'
})
export class LlmService {
  readonly api_root = 'http://localhost:1000/';
  readonly model_name='gemma3:4b'

  constructor(private http: HttpClient) {
   }

  generateScenarios(ac: string, context?: string): Observable<any> {
    const body = { model:this.model_name,question:ac}//,messages:[{role:"system",content:"You are a MobiControl Expert. Answer based on the context.\n\nContext: "+context},{role:"user",content:ac}] };

    console.log("lets generate");
    return this.getStreamPost(this.api_root+'chat', body);
    // var responses= this.http.post<any[]>(this.api_root+'api/chat', body, { observe: 'body', responseType: 'json' }).pipe(
    //   tap(rawResponse => {
    //     console.log('Raw API response:', rawResponse);
    //   }),
    //   // Process the raw response: split by newline and parse each JSON object
    //   map(rawResponse => {
    //     // Ensure rawResponse is a string before splitting
    //     const responseText = rawResponse.join('\n');
    //     // Split the text into lines (filtering out empty lines)
    //     const lines = responseText.split('\n').filter(line => line.trim().length > 0);
    //     // Parse each line as JSON
    //     const parsedResponses = lines.map(line => {
    //       try {
    //         return JSON.parse(line);
    //       } catch (e) {
    //         console.error('Error parsing JSON line:', line, e);
    //         return null;
    //       }
    //     });
    //     // Remove any null responses due to parsing errors
    //     return parsedResponses.filter(response => response !== null);
    //   }),
    //   // Log the parsed responses for debugging
    //   tap(parsedResponses => {
    //     console.log('Parsed chat responses:', parsedResponses);
    //   })
    // );
    // responses.forEach((response)=>{console.log(response)});
    // return responses;
  }
  getStreamPost(url: string, postData: any): Observable<any> {
    const data=JSON.stringify(postData);
    console.log(data);
    return new Observable<any>(observer => {
      console.log("fetching");
      fetch(url, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: data
      })
        .then(response => {
          if (!response.body) {
            throw new Error('ReadableStream not supported in this browser.');
          }
          const reader = response.body.getReader();
          const decoder = new TextDecoder();
          let buffer = '';

          const readChunk = (): void => {
            reader.read().then(({ done, value }) => {
              if (done) {
                // Process any remaining buffered text.
                if (buffer.trim().length) {
                  try {
                    observer.next(buffer);
                  } catch (e) {
                    observer.error('Error parsing final chunk: ' + e);
                  }
                }
                observer.complete();
                return;
              }
              // Decode the current chunk and append to buffer.
              buffer = decoder.decode(value, { stream: true });
              observer.next(buffer);
              // Split the buffer by newlines (assuming JSON objects are newline separated).
              // const lines = buffer.split('\n');
              // // The last line may be incomplete; keep it in the buffer.
              // buffer = lines.pop() || '';

              // // Process each complete line.
              // lines.forEach(line => {
              //   if (line.trim().length) {
              //     try {
              //       // const parsed = JSON.parse(line);
              //       // console.log(parsed);
              //       observer.next(line);
              //     } catch (e) {
              //       console.error('Error parsing JSON line:', line, e);
              //     }
              //   }
              // });

              // Read the next chunk.
              readChunk();
            }).catch(error => {
              observer.error(error);
            });
          };

          readChunk();
        })
        .catch(error => {
          observer.error(error);
        });
    });
  }
  regenerateScenarios(ac: string, context?: string): Observable<any[]> {
    // TODO: Request an alternative set of test scenarios from the LLM.
    return of([]);
  }

  generateMoreScenarios(ac: string, context?: string): Observable<any[]> {
    // TODO: Retrieve additional test scenarios to supplement the existing ones.
    return of([]);
  }

  getSourcesForScenario(scenarioId: string): Observable<any[]> {
    // TODO: Obtain source details for the specified scenario.
    return of([]);
  }
}
