# Cost Analysis

## Embeddings

### Test
We wanted to test the costs of embedding 10 10-k documents

We used the following companies for the test:

UEC - Uranium Energy Corp
DAL - Delta Airlines
NKLA - Nikola Motors
DJT - Trump Media & Technology Group
SHW - Sherwin-Williams Co
BA - Boeing
ONON - On Holding AG
WMT - Walmart
WTB - Whitbread plc (London Stock exchange)
MO - Altria Group

### Result
1,409,151 tokens embedded for $0.14

$0.01 for 100,000 tokens as [advertised by OpenAI](https://openai.com/api/pricing/?_fsi=iYuf3ay2)

__AVG 176.143 tokens per filing__ or __$0.017 per filing__

#### Number of embeddings per dollar: 58.824
 <math xmlns="http://www.w3.org/1998/Math/MathML" display="block"><semantics><mrow><mi>__58.824__</mi><mfrac><mi>__embeddings__</mi><mi>__\$__</mi></mfrac></mrow><annotation encoding="application/x-tex">\frac{messages}{\$}
</annotation></semantics></math>

## Chatting
Used model: __GPT-3.5-turbo-0125__ 
|Context size |Max output |Training data |
| -- | -- | -- |
|16,385 tokens|	4,096 tokens|	Up to Sep 2021|




### Pricing table as advertised by OpenAI
|Model|Input|Output|
| -- | -- | -- |
|gpt-3.5-turbo-0125|$0.50 / 1M tokens|$1.50 / 1M tokens|

Chain:

RAG 
Public Agent
Combinator

### Test
Test prompt: __What is the market segmentation of the company?__

### Result 
Total token usage: __7,275__ (Input: __6,280__, Output: __995__) + __28 embeddings tokens for RAG__


Cost: __<$0.01__ 

Estimate with respect to advertised prices: __\$0.0036403__ (Input: __\$0.00314__, Output: __\$0.0004975__, Embeddings: __\$0.0000028__) 

#### Number of messages per dollar: 274.703
 <math xmlns="http://www.w3.org/1998/Math/MathML" display="block"><semantics><mrow><mi>__274.703__</mi><mfrac><mi>__messages__</mi><mi>__\$__</mi></mfrac></mrow><annotation encoding="application/x-tex">\frac{messages}{\$}
</annotation></semantics></math>



