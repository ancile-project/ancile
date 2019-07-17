# Policy Visualizer

## Structure

The policy visualizer is split into two parts:

* `visualizer.py`: parses raw policy and generates flowchart representation
* `visualizer.js`: sends policy to the parser and uses MermaidJS to visualize it on the webpage in real time

## Functionality

### `visualizer.py`

For convenience, we introduce two simple classes:
*  ```Node```: represents a regular function in the policy
* ```SpecialNode```: represents a loop clause with the highest and lowest nodes saved

These are the steps:

1. ```parse_policy``` receives a raw policy string
2. ```PolicyParser.parse_it``` is called to parse the policy
3. If ```ParseError``` is raised, program exits and responds with the traceback. Otherwise, ```traverse_tree``` is called on the parsed policy
4. Using the generated tree, ```visualize_policies``` generates a MermaidJS flowchart representation
5. The flowchart is sent back in the response

### `visualizer.js`

1. An `input` event listener is added to the ```policyArea``` element in the webpage
2. Whenever a keystroke is detected in ```policyArea```, ```updateVisualization``` is called
3. An HTTP request is made with the ```policyArea``` content
4. When the request is complete, ```processResponse``` checks the response status and calls mermaid to update the visualization using the response body text
