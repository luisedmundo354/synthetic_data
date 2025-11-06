[![accord project](https://img.shields.io/badge/powered%20by-accord%20project-19C6C8.svg)](https://www.accordproject.org/)

# Accord Protocol Template: second-amendment-assignment

This template models a "Second Amendment and Assignment to Convertible Promissory Note". Executing the clause calculates the number of common shares that should be issued by dividing the `conversionAmount` from the contract by the `newConversionPrice`.

### Parse
Use the `cicero parse` command to load the template from disk and parse a contract text instance.

```
cicero parse --template ./second-amendment-assignment/ --dsl ./second-amendment-assignment/text/sample.md
```

If the sample text parses successfully you will see the JSON representation of the contract data.

### Execute
Use the `cicero execute` command to instantiate the clause using the sample text and invoke it with the default request.

```
cicero execute --template ./second-amendment-assignment/ --dsl ./second-amendment-assignment/text/sample.md --data ./second-amendment-assignment/request.json
```

The result should include a response similar to:

```
{
  "$class": "secondamendment@1.0.0.ComputeSharesResponse",
  "shares": 500000,
  "transactionId": "...",
  "timestamp": "..."
}
```

`shares` is calculated as `conversionAmount / newConversionPrice`, using the values from the parsed contract data.
