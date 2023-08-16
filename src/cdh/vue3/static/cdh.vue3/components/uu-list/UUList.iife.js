var UUList = function(vue) {
  "use strict";
  let getRandomValues;
  const rnds8 = new Uint8Array(16);
  function rng() {
    if (!getRandomValues) {
      getRandomValues = typeof crypto !== "undefined" && crypto.getRandomValues && crypto.getRandomValues.bind(crypto);
      if (!getRandomValues) {
        throw new Error("crypto.getRandomValues() not supported. See https://github.com/uuidjs/uuid#getrandomvalues-not-supported");
      }
    }
    return getRandomValues(rnds8);
  }
  const byteToHex = [];
  for (let i = 0; i < 256; ++i) {
    byteToHex.push((i + 256).toString(16).slice(1));
  }
  function unsafeStringify(arr, offset = 0) {
    return (byteToHex[arr[offset + 0]] + byteToHex[arr[offset + 1]] + byteToHex[arr[offset + 2]] + byteToHex[arr[offset + 3]] + "-" + byteToHex[arr[offset + 4]] + byteToHex[arr[offset + 5]] + "-" + byteToHex[arr[offset + 6]] + byteToHex[arr[offset + 7]] + "-" + byteToHex[arr[offset + 8]] + byteToHex[arr[offset + 9]] + "-" + byteToHex[arr[offset + 10]] + byteToHex[arr[offset + 11]] + byteToHex[arr[offset + 12]] + byteToHex[arr[offset + 13]] + byteToHex[arr[offset + 14]] + byteToHex[arr[offset + 15]]).toLowerCase();
  }
  const randomUUID = typeof crypto !== "undefined" && crypto.randomUUID && crypto.randomUUID.bind(crypto);
  const native = {
    randomUUID
  };
  function v4(options, buf, offset) {
    if (native.randomUUID && !buf && !options) {
      return native.randomUUID();
    }
    options = options || {};
    const rnds = options.random || (options.rng || rng)();
    rnds[6] = rnds[6] & 15 | 64;
    rnds[8] = rnds[8] & 63 | 128;
    if (buf) {
      offset = offset || 0;
      for (let i = 0; i < 16; ++i) {
        buf[offset + i] = rnds[i];
      }
      return buf;
    }
    return unsafeStringify(rnds);
  }
  /*!
    * shared v9.5.0
    * (c) 2023 kazuya kawaguchi
    * Released under the MIT License.
    */
  const inBrowser = typeof window !== "undefined";
  let mark;
  let measure;
  if ({}.NODE_ENV !== "production") {
    const perf = inBrowser && window.performance;
    if (perf && perf.mark && perf.measure && perf.clearMarks && // @ts-ignore browser compat
    perf.clearMeasures) {
      mark = (tag) => {
        perf.mark(tag);
      };
      measure = (name, startTag, endTag) => {
        perf.measure(name, startTag, endTag);
        perf.clearMarks(startTag);
        perf.clearMarks(endTag);
      };
    }
  }
  const RE_ARGS$1 = /\{([0-9a-zA-Z]+)\}/g;
  function format$2(message, ...args) {
    if (args.length === 1 && isObject$1(args[0])) {
      args = args[0];
    }
    if (!args || !args.hasOwnProperty) {
      args = {};
    }
    return message.replace(RE_ARGS$1, (match, identifier) => {
      return args.hasOwnProperty(identifier) ? args[identifier] : "";
    });
  }
  const makeSymbol = (name, shareable = false) => !shareable ? Symbol(name) : Symbol.for(name);
  const generateFormatCacheKey = (locale, key, source) => friendlyJSONstringify({ l: locale, k: key, s: source });
  const friendlyJSONstringify = (json) => JSON.stringify(json).replace(/\u2028/g, "\\u2028").replace(/\u2029/g, "\\u2029").replace(/\u0027/g, "\\u0027");
  const isNumber = (val) => typeof val === "number" && isFinite(val);
  const isDate = (val) => toTypeString(val) === "[object Date]";
  const isRegExp = (val) => toTypeString(val) === "[object RegExp]";
  const isEmptyObject = (val) => isPlainObject(val) && Object.keys(val).length === 0;
  const assign$1 = Object.assign;
  let _globalThis;
  const getGlobalThis = () => {
    return _globalThis || (_globalThis = typeof globalThis !== "undefined" ? globalThis : typeof self !== "undefined" ? self : typeof window !== "undefined" ? window : typeof global !== "undefined" ? global : {});
  };
  function escapeHtml(rawText) {
    return rawText.replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;").replace(/'/g, "&apos;");
  }
  const hasOwnProperty = Object.prototype.hasOwnProperty;
  function hasOwn(obj, key) {
    return hasOwnProperty.call(obj, key);
  }
  const isArray = Array.isArray;
  const isFunction = (val) => typeof val === "function";
  const isString$1 = (val) => typeof val === "string";
  const isBoolean = (val) => typeof val === "boolean";
  const isObject$1 = (val) => val !== null && typeof val === "object";
  const objectToString = Object.prototype.toString;
  const toTypeString = (value) => objectToString.call(value);
  const isPlainObject = (val) => {
    if (!isObject$1(val))
      return false;
    const proto = Object.getPrototypeOf(val);
    return proto === null || proto.constructor === Object;
  };
  const toDisplayString = (val) => {
    return val == null ? "" : isArray(val) || isPlainObject(val) && val.toString === objectToString ? JSON.stringify(val, null, 2) : String(val);
  };
  function join$1(items, separator = "") {
    return items.reduce((str, item, index) => index === 0 ? str + item : str + separator + item, "");
  }
  const RANGE = 2;
  function generateCodeFrame(source, start = 0, end = source.length) {
    const lines = source.split(/\r?\n/);
    let count = 0;
    const res = [];
    for (let i = 0; i < lines.length; i++) {
      count += lines[i].length + 1;
      if (count >= start) {
        for (let j2 = i - RANGE; j2 <= i + RANGE || end > count; j2++) {
          if (j2 < 0 || j2 >= lines.length)
            continue;
          const line = j2 + 1;
          res.push(`${line}${" ".repeat(3 - String(line).length)}|  ${lines[j2]}`);
          const lineLength = lines[j2].length;
          if (j2 === i) {
            const pad = start - (count - lineLength) + 1;
            const length = Math.max(1, end > count ? lineLength - pad : end - start);
            res.push(`   |  ` + " ".repeat(pad) + "^".repeat(length));
          } else if (j2 > i) {
            if (end > count) {
              const length = Math.max(Math.min(end - count, lineLength), 1);
              res.push(`   |  ` + "^".repeat(length));
            }
            count += lineLength + 1;
          }
        }
        break;
      }
    }
    return res.join("\n");
  }
  function incrementer(code2) {
    let current = code2;
    return () => ++current;
  }
  function warn(msg, err) {
    if (typeof console !== "undefined") {
      console.warn(`[intlify] ` + msg);
      if (err) {
        console.warn(err.stack);
      }
    }
  }
  const hasWarned = {};
  function warnOnce(msg) {
    if (!hasWarned[msg]) {
      hasWarned[msg] = true;
      warn(msg);
    }
  }
  function createEmitter() {
    const events = /* @__PURE__ */ new Map();
    const emitter = {
      events,
      on(event, handler) {
        const handlers = events.get(event);
        const added = handlers && handlers.push(handler);
        if (!added) {
          events.set(event, [handler]);
        }
      },
      off(event, handler) {
        const handlers = events.get(event);
        if (handlers) {
          handlers.splice(handlers.indexOf(handler) >>> 0, 1);
        }
      },
      emit(event, payload) {
        (events.get(event) || []).slice().map((handler) => handler(payload));
        (events.get("*") || []).slice().map((handler) => handler(event, payload));
      }
    };
    return emitter;
  }
  /*!
    * message-compiler v9.5.0
    * (c) 2023 kazuya kawaguchi
    * Released under the MIT License.
    */
  function createPosition(line, column, offset) {
    return { line, column, offset };
  }
  function createLocation(start, end, source) {
    const loc = { start, end };
    if (source != null) {
      loc.source = source;
    }
    return loc;
  }
  const RE_ARGS = /\{([0-9a-zA-Z]+)\}/g;
  function format$1(message, ...args) {
    if (args.length === 1 && isObject(args[0])) {
      args = args[0];
    }
    if (!args || !args.hasOwnProperty) {
      args = {};
    }
    return message.replace(RE_ARGS, (match, identifier) => {
      return args.hasOwnProperty(identifier) ? args[identifier] : "";
    });
  }
  const assign = Object.assign;
  const isString = (val) => typeof val === "string";
  const isObject = (val) => val !== null && typeof val === "object";
  function join(items, separator = "") {
    return items.reduce((str, item, index) => index === 0 ? str + item : str + separator + item, "");
  }
  const CompileErrorCodes = {
    // tokenizer error codes
    EXPECTED_TOKEN: 1,
    INVALID_TOKEN_IN_PLACEHOLDER: 2,
    UNTERMINATED_SINGLE_QUOTE_IN_PLACEHOLDER: 3,
    UNKNOWN_ESCAPE_SEQUENCE: 4,
    INVALID_UNICODE_ESCAPE_SEQUENCE: 5,
    UNBALANCED_CLOSING_BRACE: 6,
    UNTERMINATED_CLOSING_BRACE: 7,
    EMPTY_PLACEHOLDER: 8,
    NOT_ALLOW_NEST_PLACEHOLDER: 9,
    INVALID_LINKED_FORMAT: 10,
    // parser error codes
    MUST_HAVE_MESSAGES_IN_PLURAL: 11,
    UNEXPECTED_EMPTY_LINKED_MODIFIER: 12,
    UNEXPECTED_EMPTY_LINKED_KEY: 13,
    UNEXPECTED_LEXICAL_ANALYSIS: 14,
    // generator error codes
    UNHANDLED_CODEGEN_NODE_TYPE: 15,
    // minifier error codes
    UNHANDLED_MINIFIER_NODE_TYPE: 16,
    // Special value for higher-order compilers to pick up the last code
    // to avoid collision of error codes. This should always be kept as the last
    // item.
    __EXTEND_POINT__: 17
  };
  const errorMessages$2 = {
    // tokenizer error messages
    [CompileErrorCodes.EXPECTED_TOKEN]: `Expected token: '{0}'`,
    [CompileErrorCodes.INVALID_TOKEN_IN_PLACEHOLDER]: `Invalid token in placeholder: '{0}'`,
    [CompileErrorCodes.UNTERMINATED_SINGLE_QUOTE_IN_PLACEHOLDER]: `Unterminated single quote in placeholder`,
    [CompileErrorCodes.UNKNOWN_ESCAPE_SEQUENCE]: `Unknown escape sequence: \\{0}`,
    [CompileErrorCodes.INVALID_UNICODE_ESCAPE_SEQUENCE]: `Invalid unicode escape sequence: {0}`,
    [CompileErrorCodes.UNBALANCED_CLOSING_BRACE]: `Unbalanced closing brace`,
    [CompileErrorCodes.UNTERMINATED_CLOSING_BRACE]: `Unterminated closing brace`,
    [CompileErrorCodes.EMPTY_PLACEHOLDER]: `Empty placeholder`,
    [CompileErrorCodes.NOT_ALLOW_NEST_PLACEHOLDER]: `Not allowed nest placeholder`,
    [CompileErrorCodes.INVALID_LINKED_FORMAT]: `Invalid linked format`,
    // parser error messages
    [CompileErrorCodes.MUST_HAVE_MESSAGES_IN_PLURAL]: `Plural must have messages`,
    [CompileErrorCodes.UNEXPECTED_EMPTY_LINKED_MODIFIER]: `Unexpected empty linked modifier`,
    [CompileErrorCodes.UNEXPECTED_EMPTY_LINKED_KEY]: `Unexpected empty linked key`,
    [CompileErrorCodes.UNEXPECTED_LEXICAL_ANALYSIS]: `Unexpected lexical analysis in token: '{0}'`,
    // generator error messages
    [CompileErrorCodes.UNHANDLED_CODEGEN_NODE_TYPE]: `unhandled codegen node type: '{0}'`,
    // minimizer error messages
    [CompileErrorCodes.UNHANDLED_MINIFIER_NODE_TYPE]: `unhandled mimifier node type: '{0}'`
  };
  function createCompileError(code2, loc, options = {}) {
    const { domain, messages, args } = options;
    const msg = format$1((messages || errorMessages$2)[code2] || "", ...args || []);
    const error = new SyntaxError(String(msg));
    error.code = code2;
    if (loc) {
      error.location = loc;
    }
    error.domain = domain;
    return error;
  }
  function defaultOnError(error) {
    throw error;
  }
  const RE_HTML_TAG = /<\/?[\w\s="/.':;#-\/]+>/;
  const detectHtmlTag = (source) => RE_HTML_TAG.test(source);
  const CHAR_SP = " ";
  const CHAR_CR = "\r";
  const CHAR_LF = "\n";
  const CHAR_LS = String.fromCharCode(8232);
  const CHAR_PS = String.fromCharCode(8233);
  function createScanner(str) {
    const _buf = str;
    let _index = 0;
    let _line = 1;
    let _column = 1;
    let _peekOffset = 0;
    const isCRLF = (index2) => _buf[index2] === CHAR_CR && _buf[index2 + 1] === CHAR_LF;
    const isLF = (index2) => _buf[index2] === CHAR_LF;
    const isPS = (index2) => _buf[index2] === CHAR_PS;
    const isLS = (index2) => _buf[index2] === CHAR_LS;
    const isLineEnd = (index2) => isCRLF(index2) || isLF(index2) || isPS(index2) || isLS(index2);
    const index = () => _index;
    const line = () => _line;
    const column = () => _column;
    const peekOffset = () => _peekOffset;
    const charAt = (offset) => isCRLF(offset) || isPS(offset) || isLS(offset) ? CHAR_LF : _buf[offset];
    const currentChar = () => charAt(_index);
    const currentPeek = () => charAt(_index + _peekOffset);
    function next() {
      _peekOffset = 0;
      if (isLineEnd(_index)) {
        _line++;
        _column = 0;
      }
      if (isCRLF(_index)) {
        _index++;
      }
      _index++;
      _column++;
      return _buf[_index];
    }
    function peek() {
      if (isCRLF(_index + _peekOffset)) {
        _peekOffset++;
      }
      _peekOffset++;
      return _buf[_index + _peekOffset];
    }
    function reset() {
      _index = 0;
      _line = 1;
      _column = 1;
      _peekOffset = 0;
    }
    function resetPeek(offset = 0) {
      _peekOffset = offset;
    }
    function skipToPeek() {
      const target = _index + _peekOffset;
      while (target !== _index) {
        next();
      }
      _peekOffset = 0;
    }
    return {
      index,
      line,
      column,
      peekOffset,
      charAt,
      currentChar,
      currentPeek,
      next,
      peek,
      reset,
      resetPeek,
      skipToPeek
    };
  }
  const EOF = void 0;
  const DOT = ".";
  const LITERAL_DELIMITER = "'";
  const ERROR_DOMAIN$3 = "tokenizer";
  function createTokenizer(source, options = {}) {
    const location = options.location !== false;
    const _scnr = createScanner(source);
    const currentOffset = () => _scnr.index();
    const currentPosition = () => createPosition(_scnr.line(), _scnr.column(), _scnr.index());
    const _initLoc = currentPosition();
    const _initOffset = currentOffset();
    const _context = {
      currentType: 14,
      offset: _initOffset,
      startLoc: _initLoc,
      endLoc: _initLoc,
      lastType: 14,
      lastOffset: _initOffset,
      lastStartLoc: _initLoc,
      lastEndLoc: _initLoc,
      braceNest: 0,
      inLinked: false,
      text: ""
    };
    const context = () => _context;
    const { onError } = options;
    function emitError(code2, pos, offset, ...args) {
      const ctx = context();
      pos.column += offset;
      pos.offset += offset;
      if (onError) {
        const loc = location ? createLocation(ctx.startLoc, pos) : null;
        const err = createCompileError(code2, loc, {
          domain: ERROR_DOMAIN$3,
          args
        });
        onError(err);
      }
    }
    function getToken(context2, type, value) {
      context2.endLoc = currentPosition();
      context2.currentType = type;
      const token = { type };
      if (location) {
        token.loc = createLocation(context2.startLoc, context2.endLoc);
      }
      if (value != null) {
        token.value = value;
      }
      return token;
    }
    const getEndToken = (context2) => getToken(
      context2,
      14
      /* TokenTypes.EOF */
    );
    function eat(scnr, ch) {
      if (scnr.currentChar() === ch) {
        scnr.next();
        return ch;
      } else {
        emitError(CompileErrorCodes.EXPECTED_TOKEN, currentPosition(), 0, ch);
        return "";
      }
    }
    function peekSpaces(scnr) {
      let buf = "";
      while (scnr.currentPeek() === CHAR_SP || scnr.currentPeek() === CHAR_LF) {
        buf += scnr.currentPeek();
        scnr.peek();
      }
      return buf;
    }
    function skipSpaces(scnr) {
      const buf = peekSpaces(scnr);
      scnr.skipToPeek();
      return buf;
    }
    function isIdentifierStart(ch) {
      if (ch === EOF) {
        return false;
      }
      const cc = ch.charCodeAt(0);
      return cc >= 97 && cc <= 122 || // a-z
      cc >= 65 && cc <= 90 || // A-Z
      cc === 95;
    }
    function isNumberStart(ch) {
      if (ch === EOF) {
        return false;
      }
      const cc = ch.charCodeAt(0);
      return cc >= 48 && cc <= 57;
    }
    function isNamedIdentifierStart(scnr, context2) {
      const { currentType } = context2;
      if (currentType !== 2) {
        return false;
      }
      peekSpaces(scnr);
      const ret = isIdentifierStart(scnr.currentPeek());
      scnr.resetPeek();
      return ret;
    }
    function isListIdentifierStart(scnr, context2) {
      const { currentType } = context2;
      if (currentType !== 2) {
        return false;
      }
      peekSpaces(scnr);
      const ch = scnr.currentPeek() === "-" ? scnr.peek() : scnr.currentPeek();
      const ret = isNumberStart(ch);
      scnr.resetPeek();
      return ret;
    }
    function isLiteralStart(scnr, context2) {
      const { currentType } = context2;
      if (currentType !== 2) {
        return false;
      }
      peekSpaces(scnr);
      const ret = scnr.currentPeek() === LITERAL_DELIMITER;
      scnr.resetPeek();
      return ret;
    }
    function isLinkedDotStart(scnr, context2) {
      const { currentType } = context2;
      if (currentType !== 8) {
        return false;
      }
      peekSpaces(scnr);
      const ret = scnr.currentPeek() === ".";
      scnr.resetPeek();
      return ret;
    }
    function isLinkedModifierStart(scnr, context2) {
      const { currentType } = context2;
      if (currentType !== 9) {
        return false;
      }
      peekSpaces(scnr);
      const ret = isIdentifierStart(scnr.currentPeek());
      scnr.resetPeek();
      return ret;
    }
    function isLinkedDelimiterStart(scnr, context2) {
      const { currentType } = context2;
      if (!(currentType === 8 || currentType === 12)) {
        return false;
      }
      peekSpaces(scnr);
      const ret = scnr.currentPeek() === ":";
      scnr.resetPeek();
      return ret;
    }
    function isLinkedReferStart(scnr, context2) {
      const { currentType } = context2;
      if (currentType !== 10) {
        return false;
      }
      const fn = () => {
        const ch = scnr.currentPeek();
        if (ch === "{") {
          return isIdentifierStart(scnr.peek());
        } else if (ch === "@" || ch === "%" || ch === "|" || ch === ":" || ch === "." || ch === CHAR_SP || !ch) {
          return false;
        } else if (ch === CHAR_LF) {
          scnr.peek();
          return fn();
        } else {
          return isIdentifierStart(ch);
        }
      };
      const ret = fn();
      scnr.resetPeek();
      return ret;
    }
    function isPluralStart(scnr) {
      peekSpaces(scnr);
      const ret = scnr.currentPeek() === "|";
      scnr.resetPeek();
      return ret;
    }
    function detectModuloStart(scnr) {
      const spaces = peekSpaces(scnr);
      const ret = scnr.currentPeek() === "%" && scnr.peek() === "{";
      scnr.resetPeek();
      return {
        isModulo: ret,
        hasSpace: spaces.length > 0
      };
    }
    function isTextStart(scnr, reset = true) {
      const fn = (hasSpace = false, prev = "", detectModulo = false) => {
        const ch = scnr.currentPeek();
        if (ch === "{") {
          return prev === "%" ? false : hasSpace;
        } else if (ch === "@" || !ch) {
          return prev === "%" ? true : hasSpace;
        } else if (ch === "%") {
          scnr.peek();
          return fn(hasSpace, "%", true);
        } else if (ch === "|") {
          return prev === "%" || detectModulo ? true : !(prev === CHAR_SP || prev === CHAR_LF);
        } else if (ch === CHAR_SP) {
          scnr.peek();
          return fn(true, CHAR_SP, detectModulo);
        } else if (ch === CHAR_LF) {
          scnr.peek();
          return fn(true, CHAR_LF, detectModulo);
        } else {
          return true;
        }
      };
      const ret = fn();
      reset && scnr.resetPeek();
      return ret;
    }
    function takeChar(scnr, fn) {
      const ch = scnr.currentChar();
      if (ch === EOF) {
        return EOF;
      }
      if (fn(ch)) {
        scnr.next();
        return ch;
      }
      return null;
    }
    function takeIdentifierChar(scnr) {
      const closure = (ch) => {
        const cc = ch.charCodeAt(0);
        return cc >= 97 && cc <= 122 || // a-z
        cc >= 65 && cc <= 90 || // A-Z
        cc >= 48 && cc <= 57 || // 0-9
        cc === 95 || // _
        cc === 36;
      };
      return takeChar(scnr, closure);
    }
    function takeDigit(scnr) {
      const closure = (ch) => {
        const cc = ch.charCodeAt(0);
        return cc >= 48 && cc <= 57;
      };
      return takeChar(scnr, closure);
    }
    function takeHexDigit(scnr) {
      const closure = (ch) => {
        const cc = ch.charCodeAt(0);
        return cc >= 48 && cc <= 57 || // 0-9
        cc >= 65 && cc <= 70 || // A-F
        cc >= 97 && cc <= 102;
      };
      return takeChar(scnr, closure);
    }
    function getDigits(scnr) {
      let ch = "";
      let num = "";
      while (ch = takeDigit(scnr)) {
        num += ch;
      }
      return num;
    }
    function readModulo(scnr) {
      skipSpaces(scnr);
      const ch = scnr.currentChar();
      if (ch !== "%") {
        emitError(CompileErrorCodes.EXPECTED_TOKEN, currentPosition(), 0, ch);
      }
      scnr.next();
      return "%";
    }
    function readText(scnr) {
      let buf = "";
      while (true) {
        const ch = scnr.currentChar();
        if (ch === "{" || ch === "}" || ch === "@" || ch === "|" || !ch) {
          break;
        } else if (ch === "%") {
          if (isTextStart(scnr)) {
            buf += ch;
            scnr.next();
          } else {
            break;
          }
        } else if (ch === CHAR_SP || ch === CHAR_LF) {
          if (isTextStart(scnr)) {
            buf += ch;
            scnr.next();
          } else if (isPluralStart(scnr)) {
            break;
          } else {
            buf += ch;
            scnr.next();
          }
        } else {
          buf += ch;
          scnr.next();
        }
      }
      return buf;
    }
    function readNamedIdentifier(scnr) {
      skipSpaces(scnr);
      let ch = "";
      let name = "";
      while (ch = takeIdentifierChar(scnr)) {
        name += ch;
      }
      if (scnr.currentChar() === EOF) {
        emitError(CompileErrorCodes.UNTERMINATED_CLOSING_BRACE, currentPosition(), 0);
      }
      return name;
    }
    function readListIdentifier(scnr) {
      skipSpaces(scnr);
      let value = "";
      if (scnr.currentChar() === "-") {
        scnr.next();
        value += `-${getDigits(scnr)}`;
      } else {
        value += getDigits(scnr);
      }
      if (scnr.currentChar() === EOF) {
        emitError(CompileErrorCodes.UNTERMINATED_CLOSING_BRACE, currentPosition(), 0);
      }
      return value;
    }
    function readLiteral(scnr) {
      skipSpaces(scnr);
      eat(scnr, `'`);
      let ch = "";
      let literal = "";
      const fn = (x2) => x2 !== LITERAL_DELIMITER && x2 !== CHAR_LF;
      while (ch = takeChar(scnr, fn)) {
        if (ch === "\\") {
          literal += readEscapeSequence(scnr);
        } else {
          literal += ch;
        }
      }
      const current = scnr.currentChar();
      if (current === CHAR_LF || current === EOF) {
        emitError(CompileErrorCodes.UNTERMINATED_SINGLE_QUOTE_IN_PLACEHOLDER, currentPosition(), 0);
        if (current === CHAR_LF) {
          scnr.next();
          eat(scnr, `'`);
        }
        return literal;
      }
      eat(scnr, `'`);
      return literal;
    }
    function readEscapeSequence(scnr) {
      const ch = scnr.currentChar();
      switch (ch) {
        case "\\":
        case `'`:
          scnr.next();
          return `\\${ch}`;
        case "u":
          return readUnicodeEscapeSequence(scnr, ch, 4);
        case "U":
          return readUnicodeEscapeSequence(scnr, ch, 6);
        default:
          emitError(CompileErrorCodes.UNKNOWN_ESCAPE_SEQUENCE, currentPosition(), 0, ch);
          return "";
      }
    }
    function readUnicodeEscapeSequence(scnr, unicode, digits) {
      eat(scnr, unicode);
      let sequence = "";
      for (let i = 0; i < digits; i++) {
        const ch = takeHexDigit(scnr);
        if (!ch) {
          emitError(CompileErrorCodes.INVALID_UNICODE_ESCAPE_SEQUENCE, currentPosition(), 0, `\\${unicode}${sequence}${scnr.currentChar()}`);
          break;
        }
        sequence += ch;
      }
      return `\\${unicode}${sequence}`;
    }
    function readInvalidIdentifier(scnr) {
      skipSpaces(scnr);
      let ch = "";
      let identifiers = "";
      const closure = (ch2) => ch2 !== "{" && ch2 !== "}" && ch2 !== CHAR_SP && ch2 !== CHAR_LF;
      while (ch = takeChar(scnr, closure)) {
        identifiers += ch;
      }
      return identifiers;
    }
    function readLinkedModifier(scnr) {
      let ch = "";
      let name = "";
      while (ch = takeIdentifierChar(scnr)) {
        name += ch;
      }
      return name;
    }
    function readLinkedRefer(scnr) {
      const fn = (detect = false, buf) => {
        const ch = scnr.currentChar();
        if (ch === "{" || ch === "%" || ch === "@" || ch === "|" || ch === "(" || ch === ")" || !ch) {
          return buf;
        } else if (ch === CHAR_SP) {
          return buf;
        } else if (ch === CHAR_LF || ch === DOT) {
          buf += ch;
          scnr.next();
          return fn(detect, buf);
        } else {
          buf += ch;
          scnr.next();
          return fn(true, buf);
        }
      };
      return fn(false, "");
    }
    function readPlural(scnr) {
      skipSpaces(scnr);
      const plural = eat(
        scnr,
        "|"
        /* TokenChars.Pipe */
      );
      skipSpaces(scnr);
      return plural;
    }
    function readTokenInPlaceholder(scnr, context2) {
      let token = null;
      const ch = scnr.currentChar();
      switch (ch) {
        case "{":
          if (context2.braceNest >= 1) {
            emitError(CompileErrorCodes.NOT_ALLOW_NEST_PLACEHOLDER, currentPosition(), 0);
          }
          scnr.next();
          token = getToken(
            context2,
            2,
            "{"
            /* TokenChars.BraceLeft */
          );
          skipSpaces(scnr);
          context2.braceNest++;
          return token;
        case "}":
          if (context2.braceNest > 0 && context2.currentType === 2) {
            emitError(CompileErrorCodes.EMPTY_PLACEHOLDER, currentPosition(), 0);
          }
          scnr.next();
          token = getToken(
            context2,
            3,
            "}"
            /* TokenChars.BraceRight */
          );
          context2.braceNest--;
          context2.braceNest > 0 && skipSpaces(scnr);
          if (context2.inLinked && context2.braceNest === 0) {
            context2.inLinked = false;
          }
          return token;
        case "@":
          if (context2.braceNest > 0) {
            emitError(CompileErrorCodes.UNTERMINATED_CLOSING_BRACE, currentPosition(), 0);
          }
          token = readTokenInLinked(scnr, context2) || getEndToken(context2);
          context2.braceNest = 0;
          return token;
        default:
          let validNamedIdentifier = true;
          let validListIdentifier = true;
          let validLiteral = true;
          if (isPluralStart(scnr)) {
            if (context2.braceNest > 0) {
              emitError(CompileErrorCodes.UNTERMINATED_CLOSING_BRACE, currentPosition(), 0);
            }
            token = getToken(context2, 1, readPlural(scnr));
            context2.braceNest = 0;
            context2.inLinked = false;
            return token;
          }
          if (context2.braceNest > 0 && (context2.currentType === 5 || context2.currentType === 6 || context2.currentType === 7)) {
            emitError(CompileErrorCodes.UNTERMINATED_CLOSING_BRACE, currentPosition(), 0);
            context2.braceNest = 0;
            return readToken(scnr, context2);
          }
          if (validNamedIdentifier = isNamedIdentifierStart(scnr, context2)) {
            token = getToken(context2, 5, readNamedIdentifier(scnr));
            skipSpaces(scnr);
            return token;
          }
          if (validListIdentifier = isListIdentifierStart(scnr, context2)) {
            token = getToken(context2, 6, readListIdentifier(scnr));
            skipSpaces(scnr);
            return token;
          }
          if (validLiteral = isLiteralStart(scnr, context2)) {
            token = getToken(context2, 7, readLiteral(scnr));
            skipSpaces(scnr);
            return token;
          }
          if (!validNamedIdentifier && !validListIdentifier && !validLiteral) {
            token = getToken(context2, 13, readInvalidIdentifier(scnr));
            emitError(CompileErrorCodes.INVALID_TOKEN_IN_PLACEHOLDER, currentPosition(), 0, token.value);
            skipSpaces(scnr);
            return token;
          }
          break;
      }
      return token;
    }
    function readTokenInLinked(scnr, context2) {
      const { currentType } = context2;
      let token = null;
      const ch = scnr.currentChar();
      if ((currentType === 8 || currentType === 9 || currentType === 12 || currentType === 10) && (ch === CHAR_LF || ch === CHAR_SP)) {
        emitError(CompileErrorCodes.INVALID_LINKED_FORMAT, currentPosition(), 0);
      }
      switch (ch) {
        case "@":
          scnr.next();
          token = getToken(
            context2,
            8,
            "@"
            /* TokenChars.LinkedAlias */
          );
          context2.inLinked = true;
          return token;
        case ".":
          skipSpaces(scnr);
          scnr.next();
          return getToken(
            context2,
            9,
            "."
            /* TokenChars.LinkedDot */
          );
        case ":":
          skipSpaces(scnr);
          scnr.next();
          return getToken(
            context2,
            10,
            ":"
            /* TokenChars.LinkedDelimiter */
          );
        default:
          if (isPluralStart(scnr)) {
            token = getToken(context2, 1, readPlural(scnr));
            context2.braceNest = 0;
            context2.inLinked = false;
            return token;
          }
          if (isLinkedDotStart(scnr, context2) || isLinkedDelimiterStart(scnr, context2)) {
            skipSpaces(scnr);
            return readTokenInLinked(scnr, context2);
          }
          if (isLinkedModifierStart(scnr, context2)) {
            skipSpaces(scnr);
            return getToken(context2, 12, readLinkedModifier(scnr));
          }
          if (isLinkedReferStart(scnr, context2)) {
            skipSpaces(scnr);
            if (ch === "{") {
              return readTokenInPlaceholder(scnr, context2) || token;
            } else {
              return getToken(context2, 11, readLinkedRefer(scnr));
            }
          }
          if (currentType === 8) {
            emitError(CompileErrorCodes.INVALID_LINKED_FORMAT, currentPosition(), 0);
          }
          context2.braceNest = 0;
          context2.inLinked = false;
          return readToken(scnr, context2);
      }
    }
    function readToken(scnr, context2) {
      let token = {
        type: 14
        /* TokenTypes.EOF */
      };
      if (context2.braceNest > 0) {
        return readTokenInPlaceholder(scnr, context2) || getEndToken(context2);
      }
      if (context2.inLinked) {
        return readTokenInLinked(scnr, context2) || getEndToken(context2);
      }
      const ch = scnr.currentChar();
      switch (ch) {
        case "{":
          return readTokenInPlaceholder(scnr, context2) || getEndToken(context2);
        case "}":
          emitError(CompileErrorCodes.UNBALANCED_CLOSING_BRACE, currentPosition(), 0);
          scnr.next();
          return getToken(
            context2,
            3,
            "}"
            /* TokenChars.BraceRight */
          );
        case "@":
          return readTokenInLinked(scnr, context2) || getEndToken(context2);
        default:
          if (isPluralStart(scnr)) {
            token = getToken(context2, 1, readPlural(scnr));
            context2.braceNest = 0;
            context2.inLinked = false;
            return token;
          }
          const { isModulo, hasSpace } = detectModuloStart(scnr);
          if (isModulo) {
            return hasSpace ? getToken(context2, 0, readText(scnr)) : getToken(context2, 4, readModulo(scnr));
          }
          if (isTextStart(scnr)) {
            return getToken(context2, 0, readText(scnr));
          }
          break;
      }
      return token;
    }
    function nextToken() {
      const { currentType, offset, startLoc, endLoc } = _context;
      _context.lastType = currentType;
      _context.lastOffset = offset;
      _context.lastStartLoc = startLoc;
      _context.lastEndLoc = endLoc;
      _context.offset = currentOffset();
      _context.startLoc = currentPosition();
      if (_scnr.currentChar() === EOF) {
        return getToken(
          _context,
          14
          /* TokenTypes.EOF */
        );
      }
      return readToken(_scnr, _context);
    }
    return {
      nextToken,
      currentOffset,
      currentPosition,
      context
    };
  }
  const ERROR_DOMAIN$2 = "parser";
  const KNOWN_ESCAPES = /(?:\\\\|\\'|\\u([0-9a-fA-F]{4})|\\U([0-9a-fA-F]{6}))/g;
  function fromEscapeSequence(match, codePoint4, codePoint6) {
    switch (match) {
      case `\\\\`:
        return `\\`;
      case `\\'`:
        return `'`;
      default: {
        const codePoint = parseInt(codePoint4 || codePoint6, 16);
        if (codePoint <= 55295 || codePoint >= 57344) {
          return String.fromCodePoint(codePoint);
        }
        return "�";
      }
    }
  }
  function createParser(options = {}) {
    const location = options.location !== false;
    const { onError } = options;
    function emitError(tokenzer, code2, start, offset, ...args) {
      const end = tokenzer.currentPosition();
      end.offset += offset;
      end.column += offset;
      if (onError) {
        const loc = location ? createLocation(start, end) : null;
        const err = createCompileError(code2, loc, {
          domain: ERROR_DOMAIN$2,
          args
        });
        onError(err);
      }
    }
    function startNode(type, offset, loc) {
      const node = { type };
      if (location) {
        node.start = offset;
        node.end = offset;
        node.loc = { start: loc, end: loc };
      }
      return node;
    }
    function endNode(node, offset, pos, type) {
      if (type) {
        node.type = type;
      }
      if (location) {
        node.end = offset;
        if (node.loc) {
          node.loc.end = pos;
        }
      }
    }
    function parseText(tokenizer, value) {
      const context = tokenizer.context();
      const node = startNode(3, context.offset, context.startLoc);
      node.value = value;
      endNode(node, tokenizer.currentOffset(), tokenizer.currentPosition());
      return node;
    }
    function parseList(tokenizer, index) {
      const context = tokenizer.context();
      const { lastOffset: offset, lastStartLoc: loc } = context;
      const node = startNode(5, offset, loc);
      node.index = parseInt(index, 10);
      tokenizer.nextToken();
      endNode(node, tokenizer.currentOffset(), tokenizer.currentPosition());
      return node;
    }
    function parseNamed(tokenizer, key) {
      const context = tokenizer.context();
      const { lastOffset: offset, lastStartLoc: loc } = context;
      const node = startNode(4, offset, loc);
      node.key = key;
      tokenizer.nextToken();
      endNode(node, tokenizer.currentOffset(), tokenizer.currentPosition());
      return node;
    }
    function parseLiteral(tokenizer, value) {
      const context = tokenizer.context();
      const { lastOffset: offset, lastStartLoc: loc } = context;
      const node = startNode(9, offset, loc);
      node.value = value.replace(KNOWN_ESCAPES, fromEscapeSequence);
      tokenizer.nextToken();
      endNode(node, tokenizer.currentOffset(), tokenizer.currentPosition());
      return node;
    }
    function parseLinkedModifier(tokenizer) {
      const token = tokenizer.nextToken();
      const context = tokenizer.context();
      const { lastOffset: offset, lastStartLoc: loc } = context;
      const node = startNode(8, offset, loc);
      if (token.type !== 12) {
        emitError(tokenizer, CompileErrorCodes.UNEXPECTED_EMPTY_LINKED_MODIFIER, context.lastStartLoc, 0);
        node.value = "";
        endNode(node, offset, loc);
        return {
          nextConsumeToken: token,
          node
        };
      }
      if (token.value == null) {
        emitError(tokenizer, CompileErrorCodes.UNEXPECTED_LEXICAL_ANALYSIS, context.lastStartLoc, 0, getTokenCaption(token));
      }
      node.value = token.value || "";
      endNode(node, tokenizer.currentOffset(), tokenizer.currentPosition());
      return {
        node
      };
    }
    function parseLinkedKey(tokenizer, value) {
      const context = tokenizer.context();
      const node = startNode(7, context.offset, context.startLoc);
      node.value = value;
      endNode(node, tokenizer.currentOffset(), tokenizer.currentPosition());
      return node;
    }
    function parseLinked(tokenizer) {
      const context = tokenizer.context();
      const linkedNode = startNode(6, context.offset, context.startLoc);
      let token = tokenizer.nextToken();
      if (token.type === 9) {
        const parsed = parseLinkedModifier(tokenizer);
        linkedNode.modifier = parsed.node;
        token = parsed.nextConsumeToken || tokenizer.nextToken();
      }
      if (token.type !== 10) {
        emitError(tokenizer, CompileErrorCodes.UNEXPECTED_LEXICAL_ANALYSIS, context.lastStartLoc, 0, getTokenCaption(token));
      }
      token = tokenizer.nextToken();
      if (token.type === 2) {
        token = tokenizer.nextToken();
      }
      switch (token.type) {
        case 11:
          if (token.value == null) {
            emitError(tokenizer, CompileErrorCodes.UNEXPECTED_LEXICAL_ANALYSIS, context.lastStartLoc, 0, getTokenCaption(token));
          }
          linkedNode.key = parseLinkedKey(tokenizer, token.value || "");
          break;
        case 5:
          if (token.value == null) {
            emitError(tokenizer, CompileErrorCodes.UNEXPECTED_LEXICAL_ANALYSIS, context.lastStartLoc, 0, getTokenCaption(token));
          }
          linkedNode.key = parseNamed(tokenizer, token.value || "");
          break;
        case 6:
          if (token.value == null) {
            emitError(tokenizer, CompileErrorCodes.UNEXPECTED_LEXICAL_ANALYSIS, context.lastStartLoc, 0, getTokenCaption(token));
          }
          linkedNode.key = parseList(tokenizer, token.value || "");
          break;
        case 7:
          if (token.value == null) {
            emitError(tokenizer, CompileErrorCodes.UNEXPECTED_LEXICAL_ANALYSIS, context.lastStartLoc, 0, getTokenCaption(token));
          }
          linkedNode.key = parseLiteral(tokenizer, token.value || "");
          break;
        default:
          emitError(tokenizer, CompileErrorCodes.UNEXPECTED_EMPTY_LINKED_KEY, context.lastStartLoc, 0);
          const nextContext = tokenizer.context();
          const emptyLinkedKeyNode = startNode(7, nextContext.offset, nextContext.startLoc);
          emptyLinkedKeyNode.value = "";
          endNode(emptyLinkedKeyNode, nextContext.offset, nextContext.startLoc);
          linkedNode.key = emptyLinkedKeyNode;
          endNode(linkedNode, nextContext.offset, nextContext.startLoc);
          return {
            nextConsumeToken: token,
            node: linkedNode
          };
      }
      endNode(linkedNode, tokenizer.currentOffset(), tokenizer.currentPosition());
      return {
        node: linkedNode
      };
    }
    function parseMessage(tokenizer) {
      const context = tokenizer.context();
      const startOffset = context.currentType === 1 ? tokenizer.currentOffset() : context.offset;
      const startLoc = context.currentType === 1 ? context.endLoc : context.startLoc;
      const node = startNode(2, startOffset, startLoc);
      node.items = [];
      let nextToken = null;
      do {
        const token = nextToken || tokenizer.nextToken();
        nextToken = null;
        switch (token.type) {
          case 0:
            if (token.value == null) {
              emitError(tokenizer, CompileErrorCodes.UNEXPECTED_LEXICAL_ANALYSIS, context.lastStartLoc, 0, getTokenCaption(token));
            }
            node.items.push(parseText(tokenizer, token.value || ""));
            break;
          case 6:
            if (token.value == null) {
              emitError(tokenizer, CompileErrorCodes.UNEXPECTED_LEXICAL_ANALYSIS, context.lastStartLoc, 0, getTokenCaption(token));
            }
            node.items.push(parseList(tokenizer, token.value || ""));
            break;
          case 5:
            if (token.value == null) {
              emitError(tokenizer, CompileErrorCodes.UNEXPECTED_LEXICAL_ANALYSIS, context.lastStartLoc, 0, getTokenCaption(token));
            }
            node.items.push(parseNamed(tokenizer, token.value || ""));
            break;
          case 7:
            if (token.value == null) {
              emitError(tokenizer, CompileErrorCodes.UNEXPECTED_LEXICAL_ANALYSIS, context.lastStartLoc, 0, getTokenCaption(token));
            }
            node.items.push(parseLiteral(tokenizer, token.value || ""));
            break;
          case 8:
            const parsed = parseLinked(tokenizer);
            node.items.push(parsed.node);
            nextToken = parsed.nextConsumeToken || null;
            break;
        }
      } while (context.currentType !== 14 && context.currentType !== 1);
      const endOffset = context.currentType === 1 ? context.lastOffset : tokenizer.currentOffset();
      const endLoc = context.currentType === 1 ? context.lastEndLoc : tokenizer.currentPosition();
      endNode(node, endOffset, endLoc);
      return node;
    }
    function parsePlural(tokenizer, offset, loc, msgNode) {
      const context = tokenizer.context();
      let hasEmptyMessage = msgNode.items.length === 0;
      const node = startNode(1, offset, loc);
      node.cases = [];
      node.cases.push(msgNode);
      do {
        const msg = parseMessage(tokenizer);
        if (!hasEmptyMessage) {
          hasEmptyMessage = msg.items.length === 0;
        }
        node.cases.push(msg);
      } while (context.currentType !== 14);
      if (hasEmptyMessage) {
        emitError(tokenizer, CompileErrorCodes.MUST_HAVE_MESSAGES_IN_PLURAL, loc, 0);
      }
      endNode(node, tokenizer.currentOffset(), tokenizer.currentPosition());
      return node;
    }
    function parseResource(tokenizer) {
      const context = tokenizer.context();
      const { offset, startLoc } = context;
      const msgNode = parseMessage(tokenizer);
      if (context.currentType === 14) {
        return msgNode;
      } else {
        return parsePlural(tokenizer, offset, startLoc, msgNode);
      }
    }
    function parse2(source) {
      const tokenizer = createTokenizer(source, assign({}, options));
      const context = tokenizer.context();
      const node = startNode(0, context.offset, context.startLoc);
      if (location && node.loc) {
        node.loc.source = source;
      }
      node.body = parseResource(tokenizer);
      if (options.onCacheKey) {
        node.cacheKey = options.onCacheKey(source);
      }
      if (context.currentType !== 14) {
        emitError(tokenizer, CompileErrorCodes.UNEXPECTED_LEXICAL_ANALYSIS, context.lastStartLoc, 0, source[context.offset] || "");
      }
      endNode(node, tokenizer.currentOffset(), tokenizer.currentPosition());
      return node;
    }
    return { parse: parse2 };
  }
  function getTokenCaption(token) {
    if (token.type === 14) {
      return "EOF";
    }
    const name = (token.value || "").replace(/\r?\n/gu, "\\n");
    return name.length > 10 ? name.slice(0, 9) + "…" : name;
  }
  function createTransformer(ast, options = {}) {
    const _context = {
      ast,
      helpers: /* @__PURE__ */ new Set()
    };
    const context = () => _context;
    const helper = (name) => {
      _context.helpers.add(name);
      return name;
    };
    return { context, helper };
  }
  function traverseNodes(nodes, transformer) {
    for (let i = 0; i < nodes.length; i++) {
      traverseNode(nodes[i], transformer);
    }
  }
  function traverseNode(node, transformer) {
    switch (node.type) {
      case 1:
        traverseNodes(node.cases, transformer);
        transformer.helper(
          "plural"
          /* HelperNameMap.PLURAL */
        );
        break;
      case 2:
        traverseNodes(node.items, transformer);
        break;
      case 6:
        const linked = node;
        traverseNode(linked.key, transformer);
        transformer.helper(
          "linked"
          /* HelperNameMap.LINKED */
        );
        transformer.helper(
          "type"
          /* HelperNameMap.TYPE */
        );
        break;
      case 5:
        transformer.helper(
          "interpolate"
          /* HelperNameMap.INTERPOLATE */
        );
        transformer.helper(
          "list"
          /* HelperNameMap.LIST */
        );
        break;
      case 4:
        transformer.helper(
          "interpolate"
          /* HelperNameMap.INTERPOLATE */
        );
        transformer.helper(
          "named"
          /* HelperNameMap.NAMED */
        );
        break;
    }
  }
  function transform(ast, options = {}) {
    const transformer = createTransformer(ast);
    transformer.helper(
      "normalize"
      /* HelperNameMap.NORMALIZE */
    );
    ast.body && traverseNode(ast.body, transformer);
    const context = transformer.context();
    ast.helpers = Array.from(context.helpers);
  }
  function optimize(ast) {
    const body = ast.body;
    if (body.type === 2) {
      optimizeMessageNode(body);
    } else {
      body.cases.forEach((c) => optimizeMessageNode(c));
    }
    return ast;
  }
  function optimizeMessageNode(message) {
    if (message.items.length === 1) {
      const item = message.items[0];
      if (item.type === 3 || item.type === 9) {
        message.static = item.value;
        delete item.value;
      }
    } else {
      const values = [];
      for (let i = 0; i < message.items.length; i++) {
        const item = message.items[i];
        if (!(item.type === 3 || item.type === 9)) {
          break;
        }
        if (item.value == null) {
          break;
        }
        values.push(item.value);
      }
      if (values.length === message.items.length) {
        message.static = join(values);
        for (let i = 0; i < message.items.length; i++) {
          const item = message.items[i];
          if (item.type === 3 || item.type === 9) {
            delete item.value;
          }
        }
      }
    }
  }
  const ERROR_DOMAIN$1 = "minifier";
  function minify(node) {
    node.t = node.type;
    switch (node.type) {
      case 0:
        const resource = node;
        minify(resource.body);
        resource.b = resource.body;
        delete resource.body;
        break;
      case 1:
        const plural = node;
        const cases = plural.cases;
        for (let i = 0; i < cases.length; i++) {
          minify(cases[i]);
        }
        plural.c = cases;
        delete plural.cases;
        break;
      case 2:
        const message = node;
        const items = message.items;
        for (let i = 0; i < items.length; i++) {
          minify(items[i]);
        }
        message.i = items;
        delete message.items;
        if (message.static) {
          message.s = message.static;
          delete message.static;
        }
        break;
      case 3:
      case 9:
      case 8:
      case 7:
        const valueNode = node;
        if (valueNode.value) {
          valueNode.v = valueNode.value;
          delete valueNode.value;
        }
        break;
      case 6:
        const linked = node;
        minify(linked.key);
        linked.k = linked.key;
        delete linked.key;
        if (linked.modifier) {
          minify(linked.modifier);
          linked.m = linked.modifier;
          delete linked.modifier;
        }
        break;
      case 5:
        const list = node;
        list.i = list.index;
        delete list.index;
        break;
      case 4:
        const named = node;
        named.k = named.key;
        delete named.key;
        break;
      default: {
        throw createCompileError(CompileErrorCodes.UNHANDLED_MINIFIER_NODE_TYPE, null, {
          domain: ERROR_DOMAIN$1,
          args: [node.type]
        });
      }
    }
    delete node.type;
  }
  const ERROR_DOMAIN = "parser";
  function createCodeGenerator(ast, options) {
    const { sourceMap, filename, breakLineCode, needIndent: _needIndent } = options;
    const location = options.location !== false;
    const _context = {
      filename,
      code: "",
      column: 1,
      line: 1,
      offset: 0,
      map: void 0,
      breakLineCode,
      needIndent: _needIndent,
      indentLevel: 0
    };
    if (location && ast.loc) {
      _context.source = ast.loc.source;
    }
    const context = () => _context;
    function push(code2, node) {
      _context.code += code2;
    }
    function _newline(n, withBreakLine = true) {
      const _breakLineCode = withBreakLine ? breakLineCode : "";
      push(_needIndent ? _breakLineCode + `  `.repeat(n) : _breakLineCode);
    }
    function indent(withNewLine = true) {
      const level = ++_context.indentLevel;
      withNewLine && _newline(level);
    }
    function deindent(withNewLine = true) {
      const level = --_context.indentLevel;
      withNewLine && _newline(level);
    }
    function newline() {
      _newline(_context.indentLevel);
    }
    const helper = (key) => `_${key}`;
    const needIndent = () => _context.needIndent;
    return {
      context,
      push,
      indent,
      deindent,
      newline,
      helper,
      needIndent
    };
  }
  function generateLinkedNode(generator, node) {
    const { helper } = generator;
    generator.push(`${helper(
      "linked"
      /* HelperNameMap.LINKED */
    )}(`);
    generateNode(generator, node.key);
    if (node.modifier) {
      generator.push(`, `);
      generateNode(generator, node.modifier);
      generator.push(`, _type`);
    } else {
      generator.push(`, undefined, _type`);
    }
    generator.push(`)`);
  }
  function generateMessageNode(generator, node) {
    const { helper, needIndent } = generator;
    generator.push(`${helper(
      "normalize"
      /* HelperNameMap.NORMALIZE */
    )}([`);
    generator.indent(needIndent());
    const length = node.items.length;
    for (let i = 0; i < length; i++) {
      generateNode(generator, node.items[i]);
      if (i === length - 1) {
        break;
      }
      generator.push(", ");
    }
    generator.deindent(needIndent());
    generator.push("])");
  }
  function generatePluralNode(generator, node) {
    const { helper, needIndent } = generator;
    if (node.cases.length > 1) {
      generator.push(`${helper(
        "plural"
        /* HelperNameMap.PLURAL */
      )}([`);
      generator.indent(needIndent());
      const length = node.cases.length;
      for (let i = 0; i < length; i++) {
        generateNode(generator, node.cases[i]);
        if (i === length - 1) {
          break;
        }
        generator.push(", ");
      }
      generator.deindent(needIndent());
      generator.push(`])`);
    }
  }
  function generateResource(generator, node) {
    if (node.body) {
      generateNode(generator, node.body);
    } else {
      generator.push("null");
    }
  }
  function generateNode(generator, node) {
    const { helper } = generator;
    switch (node.type) {
      case 0:
        generateResource(generator, node);
        break;
      case 1:
        generatePluralNode(generator, node);
        break;
      case 2:
        generateMessageNode(generator, node);
        break;
      case 6:
        generateLinkedNode(generator, node);
        break;
      case 8:
        generator.push(JSON.stringify(node.value), node);
        break;
      case 7:
        generator.push(JSON.stringify(node.value), node);
        break;
      case 5:
        generator.push(`${helper(
          "interpolate"
          /* HelperNameMap.INTERPOLATE */
        )}(${helper(
          "list"
          /* HelperNameMap.LIST */
        )}(${node.index}))`, node);
        break;
      case 4:
        generator.push(`${helper(
          "interpolate"
          /* HelperNameMap.INTERPOLATE */
        )}(${helper(
          "named"
          /* HelperNameMap.NAMED */
        )}(${JSON.stringify(node.key)}))`, node);
        break;
      case 9:
        generator.push(JSON.stringify(node.value), node);
        break;
      case 3:
        generator.push(JSON.stringify(node.value), node);
        break;
      default: {
        throw createCompileError(CompileErrorCodes.UNHANDLED_CODEGEN_NODE_TYPE, null, {
          domain: ERROR_DOMAIN,
          args: [node.type]
        });
      }
    }
  }
  const generate = (ast, options = {}) => {
    const mode = isString(options.mode) ? options.mode : "normal";
    const filename = isString(options.filename) ? options.filename : "message.intl";
    const sourceMap = !!options.sourceMap;
    const breakLineCode = options.breakLineCode != null ? options.breakLineCode : mode === "arrow" ? ";" : "\n";
    const needIndent = options.needIndent ? options.needIndent : mode !== "arrow";
    const helpers = ast.helpers || [];
    const generator = createCodeGenerator(ast, {
      mode,
      filename,
      sourceMap,
      breakLineCode,
      needIndent
    });
    generator.push(mode === "normal" ? `function __msg__ (ctx) {` : `(ctx) => {`);
    generator.indent(needIndent);
    if (helpers.length > 0) {
      generator.push(`const { ${join(helpers.map((s) => `${s}: _${s}`), ", ")} } = ctx`);
      generator.newline();
    }
    generator.push(`return `);
    generateNode(generator, ast);
    generator.deindent(needIndent);
    generator.push(`}`);
    delete ast.helpers;
    const { code: code2, map } = generator.context();
    return {
      ast,
      code: code2,
      map: map ? map.toJSON() : void 0
      // eslint-disable-line @typescript-eslint/no-explicit-any
    };
  };
  function baseCompile$1(source, options = {}) {
    const assignedOptions = assign({}, options);
    const jit = !!assignedOptions.jit;
    const enalbeMinify = !!assignedOptions.minify;
    const enambeOptimize = assignedOptions.optimize == null ? true : assignedOptions.optimize;
    const parser = createParser(assignedOptions);
    const ast = parser.parse(source);
    if (!jit) {
      transform(ast, assignedOptions);
      return generate(ast, assignedOptions);
    } else {
      enambeOptimize && optimize(ast);
      enalbeMinify && minify(ast);
      return { ast, code: "" };
    }
  }
  /*!
    * core-base v9.5.0
    * (c) 2023 kazuya kawaguchi
    * Released under the MIT License.
    */
  function initFeatureFlags$1() {
    if (typeof __INTLIFY_PROD_DEVTOOLS__ !== "boolean") {
      getGlobalThis().__INTLIFY_PROD_DEVTOOLS__ = false;
    }
    if (typeof __INTLIFY_JIT_COMPILATION__ !== "boolean") {
      getGlobalThis().__INTLIFY_JIT_COMPILATION__ = false;
    }
    if (typeof __INTLIFY_DROP_MESSAGE_COMPILER__ !== "boolean") {
      getGlobalThis().__INTLIFY_DROP_MESSAGE_COMPILER__ = false;
    }
  }
  const pathStateMachine = [];
  pathStateMachine[
    0
    /* States.BEFORE_PATH */
  ] = {
    [
      "w"
      /* PathCharTypes.WORKSPACE */
    ]: [
      0
      /* States.BEFORE_PATH */
    ],
    [
      "i"
      /* PathCharTypes.IDENT */
    ]: [
      3,
      0
      /* Actions.APPEND */
    ],
    [
      "["
      /* PathCharTypes.LEFT_BRACKET */
    ]: [
      4
      /* States.IN_SUB_PATH */
    ],
    [
      "o"
      /* PathCharTypes.END_OF_FAIL */
    ]: [
      7
      /* States.AFTER_PATH */
    ]
  };
  pathStateMachine[
    1
    /* States.IN_PATH */
  ] = {
    [
      "w"
      /* PathCharTypes.WORKSPACE */
    ]: [
      1
      /* States.IN_PATH */
    ],
    [
      "."
      /* PathCharTypes.DOT */
    ]: [
      2
      /* States.BEFORE_IDENT */
    ],
    [
      "["
      /* PathCharTypes.LEFT_BRACKET */
    ]: [
      4
      /* States.IN_SUB_PATH */
    ],
    [
      "o"
      /* PathCharTypes.END_OF_FAIL */
    ]: [
      7
      /* States.AFTER_PATH */
    ]
  };
  pathStateMachine[
    2
    /* States.BEFORE_IDENT */
  ] = {
    [
      "w"
      /* PathCharTypes.WORKSPACE */
    ]: [
      2
      /* States.BEFORE_IDENT */
    ],
    [
      "i"
      /* PathCharTypes.IDENT */
    ]: [
      3,
      0
      /* Actions.APPEND */
    ],
    [
      "0"
      /* PathCharTypes.ZERO */
    ]: [
      3,
      0
      /* Actions.APPEND */
    ]
  };
  pathStateMachine[
    3
    /* States.IN_IDENT */
  ] = {
    [
      "i"
      /* PathCharTypes.IDENT */
    ]: [
      3,
      0
      /* Actions.APPEND */
    ],
    [
      "0"
      /* PathCharTypes.ZERO */
    ]: [
      3,
      0
      /* Actions.APPEND */
    ],
    [
      "w"
      /* PathCharTypes.WORKSPACE */
    ]: [
      1,
      1
      /* Actions.PUSH */
    ],
    [
      "."
      /* PathCharTypes.DOT */
    ]: [
      2,
      1
      /* Actions.PUSH */
    ],
    [
      "["
      /* PathCharTypes.LEFT_BRACKET */
    ]: [
      4,
      1
      /* Actions.PUSH */
    ],
    [
      "o"
      /* PathCharTypes.END_OF_FAIL */
    ]: [
      7,
      1
      /* Actions.PUSH */
    ]
  };
  pathStateMachine[
    4
    /* States.IN_SUB_PATH */
  ] = {
    [
      "'"
      /* PathCharTypes.SINGLE_QUOTE */
    ]: [
      5,
      0
      /* Actions.APPEND */
    ],
    [
      '"'
      /* PathCharTypes.DOUBLE_QUOTE */
    ]: [
      6,
      0
      /* Actions.APPEND */
    ],
    [
      "["
      /* PathCharTypes.LEFT_BRACKET */
    ]: [
      4,
      2
      /* Actions.INC_SUB_PATH_DEPTH */
    ],
    [
      "]"
      /* PathCharTypes.RIGHT_BRACKET */
    ]: [
      1,
      3
      /* Actions.PUSH_SUB_PATH */
    ],
    [
      "o"
      /* PathCharTypes.END_OF_FAIL */
    ]: 8,
    [
      "l"
      /* PathCharTypes.ELSE */
    ]: [
      4,
      0
      /* Actions.APPEND */
    ]
  };
  pathStateMachine[
    5
    /* States.IN_SINGLE_QUOTE */
  ] = {
    [
      "'"
      /* PathCharTypes.SINGLE_QUOTE */
    ]: [
      4,
      0
      /* Actions.APPEND */
    ],
    [
      "o"
      /* PathCharTypes.END_OF_FAIL */
    ]: 8,
    [
      "l"
      /* PathCharTypes.ELSE */
    ]: [
      5,
      0
      /* Actions.APPEND */
    ]
  };
  pathStateMachine[
    6
    /* States.IN_DOUBLE_QUOTE */
  ] = {
    [
      '"'
      /* PathCharTypes.DOUBLE_QUOTE */
    ]: [
      4,
      0
      /* Actions.APPEND */
    ],
    [
      "o"
      /* PathCharTypes.END_OF_FAIL */
    ]: 8,
    [
      "l"
      /* PathCharTypes.ELSE */
    ]: [
      6,
      0
      /* Actions.APPEND */
    ]
  };
  const literalValueRE = /^\s?(?:true|false|-?[\d.]+|'[^']*'|"[^"]*")\s?$/;
  function isLiteral(exp) {
    return literalValueRE.test(exp);
  }
  function stripQuotes(str) {
    const a = str.charCodeAt(0);
    const b = str.charCodeAt(str.length - 1);
    return a === b && (a === 34 || a === 39) ? str.slice(1, -1) : str;
  }
  function getPathCharType(ch) {
    if (ch === void 0 || ch === null) {
      return "o";
    }
    const code2 = ch.charCodeAt(0);
    switch (code2) {
      case 91:
      case 93:
      case 46:
      case 34:
      case 39:
        return ch;
      case 95:
      case 36:
      case 45:
        return "i";
      case 9:
      case 10:
      case 13:
      case 160:
      case 65279:
      case 8232:
      case 8233:
        return "w";
    }
    return "i";
  }
  function formatSubPath(path) {
    const trimmed = path.trim();
    if (path.charAt(0) === "0" && isNaN(parseInt(path))) {
      return false;
    }
    return isLiteral(trimmed) ? stripQuotes(trimmed) : "*" + trimmed;
  }
  function parse(path) {
    const keys = [];
    let index = -1;
    let mode = 0;
    let subPathDepth = 0;
    let c;
    let key;
    let newChar;
    let type;
    let transition;
    let action;
    let typeMap;
    const actions = [];
    actions[
      0
      /* Actions.APPEND */
    ] = () => {
      if (key === void 0) {
        key = newChar;
      } else {
        key += newChar;
      }
    };
    actions[
      1
      /* Actions.PUSH */
    ] = () => {
      if (key !== void 0) {
        keys.push(key);
        key = void 0;
      }
    };
    actions[
      2
      /* Actions.INC_SUB_PATH_DEPTH */
    ] = () => {
      actions[
        0
        /* Actions.APPEND */
      ]();
      subPathDepth++;
    };
    actions[
      3
      /* Actions.PUSH_SUB_PATH */
    ] = () => {
      if (subPathDepth > 0) {
        subPathDepth--;
        mode = 4;
        actions[
          0
          /* Actions.APPEND */
        ]();
      } else {
        subPathDepth = 0;
        if (key === void 0) {
          return false;
        }
        key = formatSubPath(key);
        if (key === false) {
          return false;
        } else {
          actions[
            1
            /* Actions.PUSH */
          ]();
        }
      }
    };
    function maybeUnescapeQuote() {
      const nextChar = path[index + 1];
      if (mode === 5 && nextChar === "'" || mode === 6 && nextChar === '"') {
        index++;
        newChar = "\\" + nextChar;
        actions[
          0
          /* Actions.APPEND */
        ]();
        return true;
      }
    }
    while (mode !== null) {
      index++;
      c = path[index];
      if (c === "\\" && maybeUnescapeQuote()) {
        continue;
      }
      type = getPathCharType(c);
      typeMap = pathStateMachine[mode];
      transition = typeMap[type] || typeMap[
        "l"
        /* PathCharTypes.ELSE */
      ] || 8;
      if (transition === 8) {
        return;
      }
      mode = transition[0];
      if (transition[1] !== void 0) {
        action = actions[transition[1]];
        if (action) {
          newChar = c;
          if (action() === false) {
            return;
          }
        }
      }
      if (mode === 7) {
        return keys;
      }
    }
  }
  const cache = /* @__PURE__ */ new Map();
  function resolveWithKeyValue(obj, path) {
    return isObject$1(obj) ? obj[path] : null;
  }
  function resolveValue(obj, path) {
    if (!isObject$1(obj)) {
      return null;
    }
    let hit = cache.get(path);
    if (!hit) {
      hit = parse(path);
      if (hit) {
        cache.set(path, hit);
      }
    }
    if (!hit) {
      return null;
    }
    const len = hit.length;
    let last = obj;
    let i = 0;
    while (i < len) {
      const val = last[hit[i]];
      if (val === void 0) {
        return null;
      }
      last = val;
      i++;
    }
    return last;
  }
  const DEFAULT_MODIFIER = (str) => str;
  const DEFAULT_MESSAGE = (ctx) => "";
  const DEFAULT_MESSAGE_DATA_TYPE = "text";
  const DEFAULT_NORMALIZE = (values) => values.length === 0 ? "" : join$1(values);
  const DEFAULT_INTERPOLATE = toDisplayString;
  function pluralDefault(choice, choicesLength) {
    choice = Math.abs(choice);
    if (choicesLength === 2) {
      return choice ? choice > 1 ? 1 : 0 : 1;
    }
    return choice ? Math.min(choice, 2) : 0;
  }
  function getPluralIndex(options) {
    const index = isNumber(options.pluralIndex) ? options.pluralIndex : -1;
    return options.named && (isNumber(options.named.count) || isNumber(options.named.n)) ? isNumber(options.named.count) ? options.named.count : isNumber(options.named.n) ? options.named.n : index : index;
  }
  function normalizeNamed(pluralIndex, props) {
    if (!props.count) {
      props.count = pluralIndex;
    }
    if (!props.n) {
      props.n = pluralIndex;
    }
  }
  function createMessageContext(options = {}) {
    const locale = options.locale;
    const pluralIndex = getPluralIndex(options);
    const pluralRule = isObject$1(options.pluralRules) && isString$1(locale) && isFunction(options.pluralRules[locale]) ? options.pluralRules[locale] : pluralDefault;
    const orgPluralRule = isObject$1(options.pluralRules) && isString$1(locale) && isFunction(options.pluralRules[locale]) ? pluralDefault : void 0;
    const plural = (messages) => {
      return messages[pluralRule(pluralIndex, messages.length, orgPluralRule)];
    };
    const _list = options.list || [];
    const list = (index) => _list[index];
    const _named = options.named || {};
    isNumber(options.pluralIndex) && normalizeNamed(pluralIndex, _named);
    const named = (key) => _named[key];
    function message(key) {
      const msg = isFunction(options.messages) ? options.messages(key) : isObject$1(options.messages) ? options.messages[key] : false;
      return !msg ? options.parent ? options.parent.message(key) : DEFAULT_MESSAGE : msg;
    }
    const _modifier = (name) => options.modifiers ? options.modifiers[name] : DEFAULT_MODIFIER;
    const normalize = isPlainObject(options.processor) && isFunction(options.processor.normalize) ? options.processor.normalize : DEFAULT_NORMALIZE;
    const interpolate = isPlainObject(options.processor) && isFunction(options.processor.interpolate) ? options.processor.interpolate : DEFAULT_INTERPOLATE;
    const type = isPlainObject(options.processor) && isString$1(options.processor.type) ? options.processor.type : DEFAULT_MESSAGE_DATA_TYPE;
    const linked = (key, ...args) => {
      const [arg1, arg2] = args;
      let type2 = "text";
      let modifier = "";
      if (args.length === 1) {
        if (isObject$1(arg1)) {
          modifier = arg1.modifier || modifier;
          type2 = arg1.type || type2;
        } else if (isString$1(arg1)) {
          modifier = arg1 || modifier;
        }
      } else if (args.length === 2) {
        if (isString$1(arg1)) {
          modifier = arg1 || modifier;
        }
        if (isString$1(arg2)) {
          type2 = arg2 || type2;
        }
      }
      const ret = message(key)(ctx);
      const msg = (
        // The message in vnode resolved with linked are returned as an array by processor.nomalize
        type2 === "vnode" && isArray(ret) && modifier ? ret[0] : ret
      );
      return modifier ? _modifier(modifier)(msg, type2) : msg;
    };
    const ctx = {
      [
        "list"
        /* HelperNameMap.LIST */
      ]: list,
      [
        "named"
        /* HelperNameMap.NAMED */
      ]: named,
      [
        "plural"
        /* HelperNameMap.PLURAL */
      ]: plural,
      [
        "linked"
        /* HelperNameMap.LINKED */
      ]: linked,
      [
        "message"
        /* HelperNameMap.MESSAGE */
      ]: message,
      [
        "type"
        /* HelperNameMap.TYPE */
      ]: type,
      [
        "interpolate"
        /* HelperNameMap.INTERPOLATE */
      ]: interpolate,
      [
        "normalize"
        /* HelperNameMap.NORMALIZE */
      ]: normalize,
      [
        "values"
        /* HelperNameMap.VALUES */
      ]: assign$1({}, _list, _named)
    };
    return ctx;
  }
  let devtools = null;
  function setDevToolsHook(hook) {
    devtools = hook;
  }
  function initI18nDevTools(i18n, version, meta) {
    devtools && devtools.emit("i18n:init", {
      timestamp: Date.now(),
      i18n,
      version,
      meta
    });
  }
  const translateDevTools = /* @__PURE__ */ createDevToolsHook(
    "function:translate"
    /* IntlifyDevToolsHooks.FunctionTranslate */
  );
  function createDevToolsHook(hook) {
    return (payloads) => devtools && devtools.emit(hook, payloads);
  }
  const CoreWarnCodes = {
    NOT_FOUND_KEY: 1,
    FALLBACK_TO_TRANSLATE: 2,
    CANNOT_FORMAT_NUMBER: 3,
    FALLBACK_TO_NUMBER_FORMAT: 4,
    CANNOT_FORMAT_DATE: 5,
    FALLBACK_TO_DATE_FORMAT: 6,
    EXPERIMENTAL_CUSTOM_MESSAGE_COMPILER: 7,
    __EXTEND_POINT__: 8
  };
  const warnMessages$1 = {
    [CoreWarnCodes.NOT_FOUND_KEY]: `Not found '{key}' key in '{locale}' locale messages.`,
    [CoreWarnCodes.FALLBACK_TO_TRANSLATE]: `Fall back to translate '{key}' key with '{target}' locale.`,
    [CoreWarnCodes.CANNOT_FORMAT_NUMBER]: `Cannot format a number value due to not supported Intl.NumberFormat.`,
    [CoreWarnCodes.FALLBACK_TO_NUMBER_FORMAT]: `Fall back to number format '{key}' key with '{target}' locale.`,
    [CoreWarnCodes.CANNOT_FORMAT_DATE]: `Cannot format a date value due to not supported Intl.DateTimeFormat.`,
    [CoreWarnCodes.FALLBACK_TO_DATE_FORMAT]: `Fall back to datetime format '{key}' key with '{target}' locale.`,
    [CoreWarnCodes.EXPERIMENTAL_CUSTOM_MESSAGE_COMPILER]: `This project is using Custom Message Compiler, which is an experimental feature. It may receive breaking changes or be removed in the future.`
  };
  function getWarnMessage$1(code2, ...args) {
    return format$2(warnMessages$1[code2], ...args);
  }
  function getLocale(context, options) {
    return options.locale != null ? resolveLocale(options.locale) : resolveLocale(context.locale);
  }
  let _resolveLocale;
  function resolveLocale(locale) {
    return isString$1(locale) ? locale : _resolveLocale != null && locale.resolvedOnce ? _resolveLocale : _resolveLocale = locale();
  }
  function fallbackWithSimple(ctx, fallback, start) {
    return [.../* @__PURE__ */ new Set([
      start,
      ...isArray(fallback) ? fallback : isObject$1(fallback) ? Object.keys(fallback) : isString$1(fallback) ? [fallback] : [start]
    ])];
  }
  function fallbackWithLocaleChain(ctx, fallback, start) {
    const startLocale = isString$1(start) ? start : DEFAULT_LOCALE;
    const context = ctx;
    if (!context.__localeChainCache) {
      context.__localeChainCache = /* @__PURE__ */ new Map();
    }
    let chain = context.__localeChainCache.get(startLocale);
    if (!chain) {
      chain = [];
      let block = [start];
      while (isArray(block)) {
        block = appendBlockToChain(chain, block, fallback);
      }
      const defaults = isArray(fallback) || !isPlainObject(fallback) ? fallback : fallback["default"] ? fallback["default"] : null;
      block = isString$1(defaults) ? [defaults] : defaults;
      if (isArray(block)) {
        appendBlockToChain(chain, block, false);
      }
      context.__localeChainCache.set(startLocale, chain);
    }
    return chain;
  }
  function appendBlockToChain(chain, block, blocks) {
    let follow = true;
    for (let i = 0; i < block.length && isBoolean(follow); i++) {
      const locale = block[i];
      if (isString$1(locale)) {
        follow = appendLocaleToChain(chain, block[i], blocks);
      }
    }
    return follow;
  }
  function appendLocaleToChain(chain, locale, blocks) {
    let follow;
    const tokens = locale.split("-");
    do {
      const target = tokens.join("-");
      follow = appendItemToChain(chain, target, blocks);
      tokens.splice(-1, 1);
    } while (tokens.length && follow === true);
    return follow;
  }
  function appendItemToChain(chain, target, blocks) {
    let follow = false;
    if (!chain.includes(target)) {
      follow = true;
      if (target) {
        follow = target[target.length - 1] !== "!";
        const locale = target.replace(/!/g, "");
        chain.push(locale);
        if ((isArray(blocks) || isPlainObject(blocks)) && blocks[locale]) {
          follow = blocks[locale];
        }
      }
    }
    return follow;
  }
  const VERSION$1 = "9.5.0";
  const NOT_REOSLVED = -1;
  const DEFAULT_LOCALE = "en-US";
  const MISSING_RESOLVE_VALUE = "";
  const capitalize = (str) => `${str.charAt(0).toLocaleUpperCase()}${str.substr(1)}`;
  function getDefaultLinkedModifiers() {
    return {
      upper: (val, type) => {
        return type === "text" && isString$1(val) ? val.toUpperCase() : type === "vnode" && isObject$1(val) && "__v_isVNode" in val ? val.children.toUpperCase() : val;
      },
      lower: (val, type) => {
        return type === "text" && isString$1(val) ? val.toLowerCase() : type === "vnode" && isObject$1(val) && "__v_isVNode" in val ? val.children.toLowerCase() : val;
      },
      capitalize: (val, type) => {
        return type === "text" && isString$1(val) ? capitalize(val) : type === "vnode" && isObject$1(val) && "__v_isVNode" in val ? capitalize(val.children) : val;
      }
    };
  }
  let _compiler;
  function registerMessageCompiler(compiler) {
    _compiler = compiler;
  }
  let _resolver;
  function registerMessageResolver(resolver) {
    _resolver = resolver;
  }
  let _fallbacker;
  function registerLocaleFallbacker(fallbacker) {
    _fallbacker = fallbacker;
  }
  let _additionalMeta = null;
  const setAdditionalMeta = (meta) => {
    _additionalMeta = meta;
  };
  const getAdditionalMeta = () => _additionalMeta;
  let _fallbackContext = null;
  const setFallbackContext = (context) => {
    _fallbackContext = context;
  };
  const getFallbackContext = () => _fallbackContext;
  let _cid = 0;
  function createCoreContext(options = {}) {
    const onWarn = isFunction(options.onWarn) ? options.onWarn : warn;
    const version = isString$1(options.version) ? options.version : VERSION$1;
    const locale = isString$1(options.locale) || isFunction(options.locale) ? options.locale : DEFAULT_LOCALE;
    const _locale = isFunction(locale) ? DEFAULT_LOCALE : locale;
    const fallbackLocale = isArray(options.fallbackLocale) || isPlainObject(options.fallbackLocale) || isString$1(options.fallbackLocale) || options.fallbackLocale === false ? options.fallbackLocale : _locale;
    const messages = isPlainObject(options.messages) ? options.messages : { [_locale]: {} };
    const datetimeFormats = isPlainObject(options.datetimeFormats) ? options.datetimeFormats : { [_locale]: {} };
    const numberFormats = isPlainObject(options.numberFormats) ? options.numberFormats : { [_locale]: {} };
    const modifiers = assign$1({}, options.modifiers || {}, getDefaultLinkedModifiers());
    const pluralRules = options.pluralRules || {};
    const missing = isFunction(options.missing) ? options.missing : null;
    const missingWarn = isBoolean(options.missingWarn) || isRegExp(options.missingWarn) ? options.missingWarn : true;
    const fallbackWarn = isBoolean(options.fallbackWarn) || isRegExp(options.fallbackWarn) ? options.fallbackWarn : true;
    const fallbackFormat = !!options.fallbackFormat;
    const unresolving = !!options.unresolving;
    const postTranslation = isFunction(options.postTranslation) ? options.postTranslation : null;
    const processor = isPlainObject(options.processor) ? options.processor : null;
    const warnHtmlMessage = isBoolean(options.warnHtmlMessage) ? options.warnHtmlMessage : true;
    const escapeParameter = !!options.escapeParameter;
    const messageCompiler = isFunction(options.messageCompiler) ? options.messageCompiler : _compiler;
    if ({}.NODE_ENV !== "production" && true && true && isFunction(options.messageCompiler)) {
      warnOnce(getWarnMessage$1(CoreWarnCodes.EXPERIMENTAL_CUSTOM_MESSAGE_COMPILER));
    }
    const messageResolver = isFunction(options.messageResolver) ? options.messageResolver : _resolver || resolveWithKeyValue;
    const localeFallbacker = isFunction(options.localeFallbacker) ? options.localeFallbacker : _fallbacker || fallbackWithSimple;
    const fallbackContext = isObject$1(options.fallbackContext) ? options.fallbackContext : void 0;
    const internalOptions = options;
    const __datetimeFormatters = isObject$1(internalOptions.__datetimeFormatters) ? internalOptions.__datetimeFormatters : /* @__PURE__ */ new Map();
    const __numberFormatters = isObject$1(internalOptions.__numberFormatters) ? internalOptions.__numberFormatters : /* @__PURE__ */ new Map();
    const __meta = isObject$1(internalOptions.__meta) ? internalOptions.__meta : {};
    _cid++;
    const context = {
      version,
      cid: _cid,
      locale,
      fallbackLocale,
      messages,
      modifiers,
      pluralRules,
      missing,
      missingWarn,
      fallbackWarn,
      fallbackFormat,
      unresolving,
      postTranslation,
      processor,
      warnHtmlMessage,
      escapeParameter,
      messageCompiler,
      messageResolver,
      localeFallbacker,
      fallbackContext,
      onWarn,
      __meta
    };
    {
      context.datetimeFormats = datetimeFormats;
      context.numberFormats = numberFormats;
      context.__datetimeFormatters = __datetimeFormatters;
      context.__numberFormatters = __numberFormatters;
    }
    if ({}.NODE_ENV !== "production") {
      context.__v_emitter = internalOptions.__v_emitter != null ? internalOptions.__v_emitter : void 0;
    }
    if ({}.NODE_ENV !== "production" || __INTLIFY_PROD_DEVTOOLS__) {
      initI18nDevTools(context, version, __meta);
    }
    return context;
  }
  function isTranslateFallbackWarn(fallback, key) {
    return fallback instanceof RegExp ? fallback.test(key) : fallback;
  }
  function isTranslateMissingWarn(missing, key) {
    return missing instanceof RegExp ? missing.test(key) : missing;
  }
  function handleMissing(context, key, locale, missingWarn, type) {
    const { missing, onWarn } = context;
    if ({}.NODE_ENV !== "production") {
      const emitter = context.__v_emitter;
      if (emitter) {
        emitter.emit("missing", {
          locale,
          key,
          type,
          groupId: `${type}:${key}`
        });
      }
    }
    if (missing !== null) {
      const ret = missing(context, locale, key, type);
      return isString$1(ret) ? ret : key;
    } else {
      if ({}.NODE_ENV !== "production" && isTranslateMissingWarn(missingWarn, key)) {
        onWarn(getWarnMessage$1(CoreWarnCodes.NOT_FOUND_KEY, { key, locale }));
      }
      return key;
    }
  }
  function updateFallbackLocale(ctx, locale, fallback) {
    const context = ctx;
    context.__localeChainCache = /* @__PURE__ */ new Map();
    ctx.localeFallbacker(ctx, fallback, locale);
  }
  function format(ast) {
    const msg = (ctx) => formatParts(ctx, ast);
    return msg;
  }
  function formatParts(ctx, ast) {
    const body = ast.b || ast.body;
    if ((body.t || body.type) === 1) {
      const plural = body;
      const cases = plural.c || plural.cases;
      return ctx.plural(cases.reduce((messages, c) => [
        ...messages,
        formatMessageParts(ctx, c)
      ], []));
    } else {
      return formatMessageParts(ctx, body);
    }
  }
  function formatMessageParts(ctx, node) {
    const _static = node.s || node.static;
    if (_static) {
      return ctx.type === "text" ? _static : ctx.normalize([_static]);
    } else {
      const messages = (node.i || node.items).reduce((acm, c) => [...acm, formatMessagePart(ctx, c)], []);
      return ctx.normalize(messages);
    }
  }
  function formatMessagePart(ctx, node) {
    const type = node.t || node.type;
    switch (type) {
      case 3:
        const text = node;
        return text.v || text.value;
      case 9:
        const literal = node;
        return literal.v || literal.value;
      case 4:
        const named = node;
        return ctx.interpolate(ctx.named(named.k || named.key));
      case 5:
        const list = node;
        return ctx.interpolate(ctx.list(list.i != null ? list.i : list.index));
      case 6:
        const linked = node;
        const modifier = linked.m || linked.modifier;
        return ctx.linked(formatMessagePart(ctx, linked.k || linked.key), modifier ? formatMessagePart(ctx, modifier) : void 0, ctx.type);
      case 7:
        const linkedKey = node;
        return linkedKey.v || linkedKey.value;
      case 8:
        const linkedModifier = node;
        return linkedModifier.v || linkedModifier.value;
      default:
        throw new Error(`unhandled node type on format message part: ${type}`);
    }
  }
  const code$2 = CompileErrorCodes.__EXTEND_POINT__;
  const inc$2 = incrementer(code$2);
  const CoreErrorCodes = {
    INVALID_ARGUMENT: code$2,
    INVALID_DATE_ARGUMENT: inc$2(),
    INVALID_ISO_DATE_ARGUMENT: inc$2(),
    NOT_SUPPORT_NON_STRING_MESSAGE: inc$2(),
    __EXTEND_POINT__: inc$2()
    // 22
  };
  function createCoreError(code2) {
    return createCompileError(code2, null, {}.NODE_ENV !== "production" ? { messages: errorMessages$1 } : void 0);
  }
  const errorMessages$1 = {
    [CoreErrorCodes.INVALID_ARGUMENT]: "Invalid arguments",
    [CoreErrorCodes.INVALID_DATE_ARGUMENT]: "The date provided is an invalid Date object.Make sure your Date represents a valid date.",
    [CoreErrorCodes.INVALID_ISO_DATE_ARGUMENT]: "The argument provided is not a valid ISO date string",
    [CoreErrorCodes.NOT_SUPPORT_NON_STRING_MESSAGE]: "Not support non-string message"
  };
  const WARN_MESSAGE = `Detected HTML in '{source}' message. Recommend not using HTML messages to avoid XSS.`;
  function checkHtmlMessage(source, warnHtmlMessage) {
    if (warnHtmlMessage && detectHtmlTag(source)) {
      warn(format$2(WARN_MESSAGE, { source }));
    }
  }
  const defaultOnCacheKey = (message) => message;
  let compileCache = /* @__PURE__ */ Object.create(null);
  const isMessageAST = (val) => isObject$1(val) && (val.t === 0 || val.type === 0) && ("b" in val || "body" in val);
  function baseCompile(message, options = {}) {
    let detectError = false;
    const onError = options.onError || defaultOnError;
    options.onError = (err) => {
      detectError = true;
      onError(err);
    };
    return { ...baseCompile$1(message, options), detectError };
  }
  const compileToFunction = (message, context) => {
    if (!isString$1(message)) {
      throw createCoreError(CoreErrorCodes.NOT_SUPPORT_NON_STRING_MESSAGE);
    }
    {
      const warnHtmlMessage = isBoolean(context.warnHtmlMessage) ? context.warnHtmlMessage : true;
      ({}).NODE_ENV !== "production" && checkHtmlMessage(message, warnHtmlMessage);
      const onCacheKey = context.onCacheKey || defaultOnCacheKey;
      const cacheKey = onCacheKey(message);
      const cached = compileCache[cacheKey];
      if (cached) {
        return cached;
      }
      const { code: code2, detectError } = baseCompile(message, context);
      const msg = new Function(`return ${code2}`)();
      return !detectError ? compileCache[cacheKey] = msg : msg;
    }
  };
  function compile(message, context) {
    if (__INTLIFY_JIT_COMPILATION__ && !__INTLIFY_DROP_MESSAGE_COMPILER__ && isString$1(message)) {
      const warnHtmlMessage = isBoolean(context.warnHtmlMessage) ? context.warnHtmlMessage : true;
      ({}).NODE_ENV !== "production" && checkHtmlMessage(message, warnHtmlMessage);
      const onCacheKey = context.onCacheKey || defaultOnCacheKey;
      const cacheKey = onCacheKey(message);
      const cached = compileCache[cacheKey];
      if (cached) {
        return cached;
      }
      const { ast, detectError } = baseCompile(message, {
        ...context,
        location: {}.NODE_ENV !== "production",
        jit: true
      });
      const msg = format(ast);
      return !detectError ? compileCache[cacheKey] = msg : msg;
    } else {
      if ({}.NODE_ENV !== "production" && !isMessageAST(message)) {
        warn(`the message that is resolve with key '${context.key}' is not supported for jit compilation`);
        return () => message;
      }
      const cacheKey = message.cacheKey;
      if (cacheKey) {
        const cached = compileCache[cacheKey];
        if (cached) {
          return cached;
        }
        return compileCache[cacheKey] = format(message);
      } else {
        return format(message);
      }
    }
  }
  const NOOP_MESSAGE_FUNCTION = () => "";
  const isMessageFunction = (val) => isFunction(val);
  function translate(context, ...args) {
    const { fallbackFormat, postTranslation, unresolving, messageCompiler, fallbackLocale, messages } = context;
    const [key, options] = parseTranslateArgs(...args);
    const missingWarn = isBoolean(options.missingWarn) ? options.missingWarn : context.missingWarn;
    const fallbackWarn = isBoolean(options.fallbackWarn) ? options.fallbackWarn : context.fallbackWarn;
    const escapeParameter = isBoolean(options.escapeParameter) ? options.escapeParameter : context.escapeParameter;
    const resolvedMessage = !!options.resolvedMessage;
    const defaultMsgOrKey = isString$1(options.default) || isBoolean(options.default) ? !isBoolean(options.default) ? options.default : !messageCompiler ? () => key : key : fallbackFormat ? !messageCompiler ? () => key : key : "";
    const enableDefaultMsg = fallbackFormat || defaultMsgOrKey !== "";
    const locale = getLocale(context, options);
    escapeParameter && escapeParams(options);
    let [formatScope, targetLocale, message] = !resolvedMessage ? resolveMessageFormat(context, key, locale, fallbackLocale, fallbackWarn, missingWarn) : [
      key,
      locale,
      messages[locale] || {}
    ];
    let format2 = formatScope;
    let cacheBaseKey = key;
    if (!resolvedMessage && !(isString$1(format2) || isMessageAST(format2) || isMessageFunction(format2))) {
      if (enableDefaultMsg) {
        format2 = defaultMsgOrKey;
        cacheBaseKey = format2;
      }
    }
    if (!resolvedMessage && (!(isString$1(format2) || isMessageAST(format2) || isMessageFunction(format2)) || !isString$1(targetLocale))) {
      return unresolving ? NOT_REOSLVED : key;
    }
    if ({}.NODE_ENV !== "production" && isString$1(format2) && context.messageCompiler == null) {
      warn(`The message format compilation is not supported in this build. Because message compiler isn't included. You need to pre-compilation all message format. So translate function return '${key}'.`);
      return key;
    }
    let occurred = false;
    const onError = () => {
      occurred = true;
    };
    const msg = !isMessageFunction(format2) ? compileMessageFormat(context, key, targetLocale, format2, cacheBaseKey, onError) : format2;
    if (occurred) {
      return format2;
    }
    const ctxOptions = getMessageContextOptions(context, targetLocale, message, options);
    const msgContext = createMessageContext(ctxOptions);
    const messaged = evaluateMessage(context, msg, msgContext);
    const ret = postTranslation ? postTranslation(messaged, key) : messaged;
    if ({}.NODE_ENV !== "production" || __INTLIFY_PROD_DEVTOOLS__) {
      const payloads = {
        timestamp: Date.now(),
        key: isString$1(key) ? key : isMessageFunction(format2) ? format2.key : "",
        locale: targetLocale || (isMessageFunction(format2) ? format2.locale : ""),
        format: isString$1(format2) ? format2 : isMessageFunction(format2) ? format2.source : "",
        message: ret
      };
      payloads.meta = assign$1({}, context.__meta, getAdditionalMeta() || {});
      translateDevTools(payloads);
    }
    return ret;
  }
  function escapeParams(options) {
    if (isArray(options.list)) {
      options.list = options.list.map((item) => isString$1(item) ? escapeHtml(item) : item);
    } else if (isObject$1(options.named)) {
      Object.keys(options.named).forEach((key) => {
        if (isString$1(options.named[key])) {
          options.named[key] = escapeHtml(options.named[key]);
        }
      });
    }
  }
  function resolveMessageFormat(context, key, locale, fallbackLocale, fallbackWarn, missingWarn) {
    const { messages, onWarn, messageResolver: resolveValue2, localeFallbacker } = context;
    const locales = localeFallbacker(context, fallbackLocale, locale);
    let message = {};
    let targetLocale;
    let format2 = null;
    let from = locale;
    let to = null;
    const type = "translate";
    for (let i = 0; i < locales.length; i++) {
      targetLocale = to = locales[i];
      if ({}.NODE_ENV !== "production" && locale !== targetLocale && isTranslateFallbackWarn(fallbackWarn, key)) {
        onWarn(getWarnMessage$1(CoreWarnCodes.FALLBACK_TO_TRANSLATE, {
          key,
          target: targetLocale
        }));
      }
      if ({}.NODE_ENV !== "production" && locale !== targetLocale) {
        const emitter = context.__v_emitter;
        if (emitter) {
          emitter.emit("fallback", {
            type,
            key,
            from,
            to,
            groupId: `${type}:${key}`
          });
        }
      }
      message = messages[targetLocale] || {};
      let start = null;
      let startTag;
      let endTag;
      if ({}.NODE_ENV !== "production" && inBrowser) {
        start = window.performance.now();
        startTag = "intlify-message-resolve-start";
        endTag = "intlify-message-resolve-end";
        mark && mark(startTag);
      }
      if ((format2 = resolveValue2(message, key)) === null) {
        format2 = message[key];
      }
      if ({}.NODE_ENV !== "production" && inBrowser) {
        const end = window.performance.now();
        const emitter = context.__v_emitter;
        if (emitter && start && format2) {
          emitter.emit("message-resolve", {
            type: "message-resolve",
            key,
            message: format2,
            time: end - start,
            groupId: `${type}:${key}`
          });
        }
        if (startTag && endTag && mark && measure) {
          mark(endTag);
          measure("intlify message resolve", startTag, endTag);
        }
      }
      if (isString$1(format2) || isMessageAST(format2) || isMessageFunction(format2)) {
        break;
      }
      const missingRet = handleMissing(
        context,
        // eslint-disable-line @typescript-eslint/no-explicit-any
        key,
        targetLocale,
        missingWarn,
        type
      );
      if (missingRet !== key) {
        format2 = missingRet;
      }
      from = to;
    }
    return [format2, targetLocale, message];
  }
  function compileMessageFormat(context, key, targetLocale, format2, cacheBaseKey, onError) {
    const { messageCompiler, warnHtmlMessage } = context;
    if (isMessageFunction(format2)) {
      const msg2 = format2;
      msg2.locale = msg2.locale || targetLocale;
      msg2.key = msg2.key || key;
      return msg2;
    }
    if (messageCompiler == null) {
      const msg2 = () => format2;
      msg2.locale = targetLocale;
      msg2.key = key;
      return msg2;
    }
    let start = null;
    let startTag;
    let endTag;
    if ({}.NODE_ENV !== "production" && inBrowser) {
      start = window.performance.now();
      startTag = "intlify-message-compilation-start";
      endTag = "intlify-message-compilation-end";
      mark && mark(startTag);
    }
    const msg = messageCompiler(format2, getCompileContext(context, targetLocale, cacheBaseKey, format2, warnHtmlMessage, onError));
    if ({}.NODE_ENV !== "production" && inBrowser) {
      const end = window.performance.now();
      const emitter = context.__v_emitter;
      if (emitter && start) {
        emitter.emit("message-compilation", {
          type: "message-compilation",
          message: format2,
          time: end - start,
          groupId: `${"translate"}:${key}`
        });
      }
      if (startTag && endTag && mark && measure) {
        mark(endTag);
        measure("intlify message compilation", startTag, endTag);
      }
    }
    msg.locale = targetLocale;
    msg.key = key;
    msg.source = format2;
    return msg;
  }
  function evaluateMessage(context, msg, msgCtx) {
    let start = null;
    let startTag;
    let endTag;
    if ({}.NODE_ENV !== "production" && inBrowser) {
      start = window.performance.now();
      startTag = "intlify-message-evaluation-start";
      endTag = "intlify-message-evaluation-end";
      mark && mark(startTag);
    }
    const messaged = msg(msgCtx);
    if ({}.NODE_ENV !== "production" && inBrowser) {
      const end = window.performance.now();
      const emitter = context.__v_emitter;
      if (emitter && start) {
        emitter.emit("message-evaluation", {
          type: "message-evaluation",
          value: messaged,
          time: end - start,
          groupId: `${"translate"}:${msg.key}`
        });
      }
      if (startTag && endTag && mark && measure) {
        mark(endTag);
        measure("intlify message evaluation", startTag, endTag);
      }
    }
    return messaged;
  }
  function parseTranslateArgs(...args) {
    const [arg1, arg2, arg3] = args;
    const options = {};
    if (!isString$1(arg1) && !isNumber(arg1) && !isMessageFunction(arg1) && !isMessageAST(arg1)) {
      throw createCoreError(CoreErrorCodes.INVALID_ARGUMENT);
    }
    const key = isNumber(arg1) ? String(arg1) : isMessageFunction(arg1) ? arg1 : arg1;
    if (isNumber(arg2)) {
      options.plural = arg2;
    } else if (isString$1(arg2)) {
      options.default = arg2;
    } else if (isPlainObject(arg2) && !isEmptyObject(arg2)) {
      options.named = arg2;
    } else if (isArray(arg2)) {
      options.list = arg2;
    }
    if (isNumber(arg3)) {
      options.plural = arg3;
    } else if (isString$1(arg3)) {
      options.default = arg3;
    } else if (isPlainObject(arg3)) {
      assign$1(options, arg3);
    }
    return [key, options];
  }
  function getCompileContext(context, locale, key, source, warnHtmlMessage, onError) {
    return {
      locale,
      key,
      warnHtmlMessage,
      onError: (err) => {
        onError && onError(err);
        if ({}.NODE_ENV !== "production") {
          const _source = getSourceForCodeFrame(source);
          const message = `Message compilation error: ${err.message}`;
          const codeFrame = err.location && _source && generateCodeFrame(_source, err.location.start.offset, err.location.end.offset);
          const emitter = context.__v_emitter;
          if (emitter && _source) {
            emitter.emit("compile-error", {
              message: _source,
              error: err.message,
              start: err.location && err.location.start.offset,
              end: err.location && err.location.end.offset,
              groupId: `${"translate"}:${key}`
            });
          }
          console.error(codeFrame ? `${message}
${codeFrame}` : message);
        } else {
          throw err;
        }
      },
      onCacheKey: (source2) => generateFormatCacheKey(locale, key, source2)
    };
  }
  function getSourceForCodeFrame(source) {
    var _a;
    if (isString$1(source))
      ;
    else {
      if ((_a = source.loc) == null ? void 0 : _a.source) {
        return source.loc.source;
      }
    }
  }
  function getMessageContextOptions(context, locale, message, options) {
    const { modifiers, pluralRules, messageResolver: resolveValue2, fallbackLocale, fallbackWarn, missingWarn, fallbackContext } = context;
    const resolveMessage = (key) => {
      let val = resolveValue2(message, key);
      if (val == null && fallbackContext) {
        const [, , message2] = resolveMessageFormat(fallbackContext, key, locale, fallbackLocale, fallbackWarn, missingWarn);
        val = resolveValue2(message2, key);
      }
      if (isString$1(val) || isMessageAST(val)) {
        let occurred = false;
        const onError = () => {
          occurred = true;
        };
        const msg = compileMessageFormat(context, key, locale, val, key, onError);
        return !occurred ? msg : NOOP_MESSAGE_FUNCTION;
      } else if (isMessageFunction(val)) {
        return val;
      } else {
        return NOOP_MESSAGE_FUNCTION;
      }
    };
    const ctxOptions = {
      locale,
      modifiers,
      pluralRules,
      messages: resolveMessage
    };
    if (context.processor) {
      ctxOptions.processor = context.processor;
    }
    if (options.list) {
      ctxOptions.list = options.list;
    }
    if (options.named) {
      ctxOptions.named = options.named;
    }
    if (isNumber(options.plural)) {
      ctxOptions.pluralIndex = options.plural;
    }
    return ctxOptions;
  }
  const intlDefined = typeof Intl !== "undefined";
  const Availabilities = {
    dateTimeFormat: intlDefined && typeof Intl.DateTimeFormat !== "undefined",
    numberFormat: intlDefined && typeof Intl.NumberFormat !== "undefined"
  };
  function datetime(context, ...args) {
    const { datetimeFormats, unresolving, fallbackLocale, onWarn, localeFallbacker } = context;
    const { __datetimeFormatters } = context;
    if ({}.NODE_ENV !== "production" && !Availabilities.dateTimeFormat) {
      onWarn(getWarnMessage$1(CoreWarnCodes.CANNOT_FORMAT_DATE));
      return MISSING_RESOLVE_VALUE;
    }
    const [key, value, options, overrides] = parseDateTimeArgs(...args);
    const missingWarn = isBoolean(options.missingWarn) ? options.missingWarn : context.missingWarn;
    const fallbackWarn = isBoolean(options.fallbackWarn) ? options.fallbackWarn : context.fallbackWarn;
    const part = !!options.part;
    const locale = getLocale(context, options);
    const locales = localeFallbacker(
      context,
      // eslint-disable-line @typescript-eslint/no-explicit-any
      fallbackLocale,
      locale
    );
    if (!isString$1(key) || key === "") {
      return new Intl.DateTimeFormat(locale, overrides).format(value);
    }
    let datetimeFormat = {};
    let targetLocale;
    let format2 = null;
    let from = locale;
    let to = null;
    const type = "datetime format";
    for (let i = 0; i < locales.length; i++) {
      targetLocale = to = locales[i];
      if ({}.NODE_ENV !== "production" && locale !== targetLocale && isTranslateFallbackWarn(fallbackWarn, key)) {
        onWarn(getWarnMessage$1(CoreWarnCodes.FALLBACK_TO_DATE_FORMAT, {
          key,
          target: targetLocale
        }));
      }
      if ({}.NODE_ENV !== "production" && locale !== targetLocale) {
        const emitter = context.__v_emitter;
        if (emitter) {
          emitter.emit("fallback", {
            type,
            key,
            from,
            to,
            groupId: `${type}:${key}`
          });
        }
      }
      datetimeFormat = datetimeFormats[targetLocale] || {};
      format2 = datetimeFormat[key];
      if (isPlainObject(format2))
        break;
      handleMissing(context, key, targetLocale, missingWarn, type);
      from = to;
    }
    if (!isPlainObject(format2) || !isString$1(targetLocale)) {
      return unresolving ? NOT_REOSLVED : key;
    }
    let id = `${targetLocale}__${key}`;
    if (!isEmptyObject(overrides)) {
      id = `${id}__${JSON.stringify(overrides)}`;
    }
    let formatter = __datetimeFormatters.get(id);
    if (!formatter) {
      formatter = new Intl.DateTimeFormat(targetLocale, assign$1({}, format2, overrides));
      __datetimeFormatters.set(id, formatter);
    }
    return !part ? formatter.format(value) : formatter.formatToParts(value);
  }
  const DATETIME_FORMAT_OPTIONS_KEYS = [
    "localeMatcher",
    "weekday",
    "era",
    "year",
    "month",
    "day",
    "hour",
    "minute",
    "second",
    "timeZoneName",
    "formatMatcher",
    "hour12",
    "timeZone",
    "dateStyle",
    "timeStyle",
    "calendar",
    "dayPeriod",
    "numberingSystem",
    "hourCycle",
    "fractionalSecondDigits"
  ];
  function parseDateTimeArgs(...args) {
    const [arg1, arg2, arg3, arg4] = args;
    const options = {};
    let overrides = {};
    let value;
    if (isString$1(arg1)) {
      const matches = arg1.match(/(\d{4}-\d{2}-\d{2})(T|\s)?(.*)/);
      if (!matches) {
        throw createCoreError(CoreErrorCodes.INVALID_ISO_DATE_ARGUMENT);
      }
      const dateTime = matches[3] ? matches[3].trim().startsWith("T") ? `${matches[1].trim()}${matches[3].trim()}` : `${matches[1].trim()}T${matches[3].trim()}` : matches[1].trim();
      value = new Date(dateTime);
      try {
        value.toISOString();
      } catch (e) {
        throw createCoreError(CoreErrorCodes.INVALID_ISO_DATE_ARGUMENT);
      }
    } else if (isDate(arg1)) {
      if (isNaN(arg1.getTime())) {
        throw createCoreError(CoreErrorCodes.INVALID_DATE_ARGUMENT);
      }
      value = arg1;
    } else if (isNumber(arg1)) {
      value = arg1;
    } else {
      throw createCoreError(CoreErrorCodes.INVALID_ARGUMENT);
    }
    if (isString$1(arg2)) {
      options.key = arg2;
    } else if (isPlainObject(arg2)) {
      Object.keys(arg2).forEach((key) => {
        if (DATETIME_FORMAT_OPTIONS_KEYS.includes(key)) {
          overrides[key] = arg2[key];
        } else {
          options[key] = arg2[key];
        }
      });
    }
    if (isString$1(arg3)) {
      options.locale = arg3;
    } else if (isPlainObject(arg3)) {
      overrides = arg3;
    }
    if (isPlainObject(arg4)) {
      overrides = arg4;
    }
    return [options.key || "", value, options, overrides];
  }
  function clearDateTimeFormat(ctx, locale, format2) {
    const context = ctx;
    for (const key in format2) {
      const id = `${locale}__${key}`;
      if (!context.__datetimeFormatters.has(id)) {
        continue;
      }
      context.__datetimeFormatters.delete(id);
    }
  }
  function number(context, ...args) {
    const { numberFormats, unresolving, fallbackLocale, onWarn, localeFallbacker } = context;
    const { __numberFormatters } = context;
    if ({}.NODE_ENV !== "production" && !Availabilities.numberFormat) {
      onWarn(getWarnMessage$1(CoreWarnCodes.CANNOT_FORMAT_NUMBER));
      return MISSING_RESOLVE_VALUE;
    }
    const [key, value, options, overrides] = parseNumberArgs(...args);
    const missingWarn = isBoolean(options.missingWarn) ? options.missingWarn : context.missingWarn;
    const fallbackWarn = isBoolean(options.fallbackWarn) ? options.fallbackWarn : context.fallbackWarn;
    const part = !!options.part;
    const locale = getLocale(context, options);
    const locales = localeFallbacker(
      context,
      // eslint-disable-line @typescript-eslint/no-explicit-any
      fallbackLocale,
      locale
    );
    if (!isString$1(key) || key === "") {
      return new Intl.NumberFormat(locale, overrides).format(value);
    }
    let numberFormat = {};
    let targetLocale;
    let format2 = null;
    let from = locale;
    let to = null;
    const type = "number format";
    for (let i = 0; i < locales.length; i++) {
      targetLocale = to = locales[i];
      if ({}.NODE_ENV !== "production" && locale !== targetLocale && isTranslateFallbackWarn(fallbackWarn, key)) {
        onWarn(getWarnMessage$1(CoreWarnCodes.FALLBACK_TO_NUMBER_FORMAT, {
          key,
          target: targetLocale
        }));
      }
      if ({}.NODE_ENV !== "production" && locale !== targetLocale) {
        const emitter = context.__v_emitter;
        if (emitter) {
          emitter.emit("fallback", {
            type,
            key,
            from,
            to,
            groupId: `${type}:${key}`
          });
        }
      }
      numberFormat = numberFormats[targetLocale] || {};
      format2 = numberFormat[key];
      if (isPlainObject(format2))
        break;
      handleMissing(context, key, targetLocale, missingWarn, type);
      from = to;
    }
    if (!isPlainObject(format2) || !isString$1(targetLocale)) {
      return unresolving ? NOT_REOSLVED : key;
    }
    let id = `${targetLocale}__${key}`;
    if (!isEmptyObject(overrides)) {
      id = `${id}__${JSON.stringify(overrides)}`;
    }
    let formatter = __numberFormatters.get(id);
    if (!formatter) {
      formatter = new Intl.NumberFormat(targetLocale, assign$1({}, format2, overrides));
      __numberFormatters.set(id, formatter);
    }
    return !part ? formatter.format(value) : formatter.formatToParts(value);
  }
  const NUMBER_FORMAT_OPTIONS_KEYS = [
    "localeMatcher",
    "style",
    "currency",
    "currencyDisplay",
    "currencySign",
    "useGrouping",
    "minimumIntegerDigits",
    "minimumFractionDigits",
    "maximumFractionDigits",
    "minimumSignificantDigits",
    "maximumSignificantDigits",
    "compactDisplay",
    "notation",
    "signDisplay",
    "unit",
    "unitDisplay",
    "roundingMode",
    "roundingPriority",
    "roundingIncrement",
    "trailingZeroDisplay"
  ];
  function parseNumberArgs(...args) {
    const [arg1, arg2, arg3, arg4] = args;
    const options = {};
    let overrides = {};
    if (!isNumber(arg1)) {
      throw createCoreError(CoreErrorCodes.INVALID_ARGUMENT);
    }
    const value = arg1;
    if (isString$1(arg2)) {
      options.key = arg2;
    } else if (isPlainObject(arg2)) {
      Object.keys(arg2).forEach((key) => {
        if (NUMBER_FORMAT_OPTIONS_KEYS.includes(key)) {
          overrides[key] = arg2[key];
        } else {
          options[key] = arg2[key];
        }
      });
    }
    if (isString$1(arg3)) {
      options.locale = arg3;
    } else if (isPlainObject(arg3)) {
      overrides = arg3;
    }
    if (isPlainObject(arg4)) {
      overrides = arg4;
    }
    return [options.key || "", value, options, overrides];
  }
  function clearNumberFormat(ctx, locale, format2) {
    const context = ctx;
    for (const key in format2) {
      const id = `${locale}__${key}`;
      if (!context.__numberFormatters.has(id)) {
        continue;
      }
      context.__numberFormatters.delete(id);
    }
  }
  {
    initFeatureFlags$1();
  }
  /*!
    * vue-i18n v9.5.0
    * (c) 2023 kazuya kawaguchi
    * Released under the MIT License.
    */
  const VERSION = "9.5.0";
  function initFeatureFlags() {
    if (typeof __VUE_I18N_FULL_INSTALL__ !== "boolean") {
      getGlobalThis().__VUE_I18N_FULL_INSTALL__ = true;
    }
    if (typeof __VUE_I18N_LEGACY_API__ !== "boolean") {
      getGlobalThis().__VUE_I18N_LEGACY_API__ = true;
    }
    if (typeof __INTLIFY_JIT_COMPILATION__ !== "boolean") {
      getGlobalThis().__INTLIFY_JIT_COMPILATION__ = false;
    }
    if (typeof __INTLIFY_DROP_MESSAGE_COMPILER__ !== "boolean") {
      getGlobalThis().__INTLIFY_DROP_MESSAGE_COMPILER__ = false;
    }
    if (typeof __INTLIFY_PROD_DEVTOOLS__ !== "boolean") {
      getGlobalThis().__INTLIFY_PROD_DEVTOOLS__ = false;
    }
  }
  const code$1 = CoreWarnCodes.__EXTEND_POINT__;
  const inc$1 = incrementer(code$1);
  const I18nWarnCodes = {
    FALLBACK_TO_ROOT: code$1,
    NOT_SUPPORTED_PRESERVE: inc$1(),
    NOT_SUPPORTED_FORMATTER: inc$1(),
    NOT_SUPPORTED_PRESERVE_DIRECTIVE: inc$1(),
    NOT_SUPPORTED_GET_CHOICE_INDEX: inc$1(),
    COMPONENT_NAME_LEGACY_COMPATIBLE: inc$1(),
    NOT_FOUND_PARENT_SCOPE: inc$1(),
    IGNORE_OBJ_FLATTEN: inc$1(),
    NOTICE_DROP_ALLOW_COMPOSITION: inc$1()
    // 17
  };
  const warnMessages = {
    [I18nWarnCodes.FALLBACK_TO_ROOT]: `Fall back to {type} '{key}' with root locale.`,
    [I18nWarnCodes.NOT_SUPPORTED_PRESERVE]: `Not supported 'preserve'.`,
    [I18nWarnCodes.NOT_SUPPORTED_FORMATTER]: `Not supported 'formatter'.`,
    [I18nWarnCodes.NOT_SUPPORTED_PRESERVE_DIRECTIVE]: `Not supported 'preserveDirectiveContent'.`,
    [I18nWarnCodes.NOT_SUPPORTED_GET_CHOICE_INDEX]: `Not supported 'getChoiceIndex'.`,
    [I18nWarnCodes.COMPONENT_NAME_LEGACY_COMPATIBLE]: `Component name legacy compatible: '{name}' -> 'i18n'`,
    [I18nWarnCodes.NOT_FOUND_PARENT_SCOPE]: `Not found parent scope. use the global scope.`,
    [I18nWarnCodes.IGNORE_OBJ_FLATTEN]: `Ignore object flatten: '{key}' key has an string value`,
    [I18nWarnCodes.NOTICE_DROP_ALLOW_COMPOSITION]: `'allowComposition' option will be dropped in the next major version. For more information, please see 👉 https://tinyurl.com/2p97mcze`
  };
  function getWarnMessage(code2, ...args) {
    return format$2(warnMessages[code2], ...args);
  }
  const code = CoreErrorCodes.__EXTEND_POINT__;
  const inc = incrementer(code);
  const I18nErrorCodes = {
    // composer module errors
    UNEXPECTED_RETURN_TYPE: code,
    // legacy module errors
    INVALID_ARGUMENT: inc(),
    // i18n module errors
    MUST_BE_CALL_SETUP_TOP: inc(),
    NOT_INSTALLED: inc(),
    NOT_AVAILABLE_IN_LEGACY_MODE: inc(),
    // directive module errors
    REQUIRED_VALUE: inc(),
    INVALID_VALUE: inc(),
    // vue-devtools errors
    CANNOT_SETUP_VUE_DEVTOOLS_PLUGIN: inc(),
    NOT_INSTALLED_WITH_PROVIDE: inc(),
    // unexpected error
    UNEXPECTED_ERROR: inc(),
    // not compatible legacy vue-i18n constructor
    NOT_COMPATIBLE_LEGACY_VUE_I18N: inc(),
    // bridge support vue 2.x only
    BRIDGE_SUPPORT_VUE_2_ONLY: inc(),
    // need to define `i18n` option in `allowComposition: true` and `useScope: 'local' at `useI18n``
    MUST_DEFINE_I18N_OPTION_IN_ALLOW_COMPOSITION: inc(),
    // Not available Compostion API in Legacy API mode. Please make sure that the legacy API mode is working properly
    NOT_AVAILABLE_COMPOSITION_IN_LEGACY: inc(),
    // for enhancement
    __EXTEND_POINT__: inc()
    // 37
  };
  function createI18nError(code2, ...args) {
    return createCompileError(code2, null, {}.NODE_ENV !== "production" ? { messages: errorMessages, args } : void 0);
  }
  const errorMessages = {
    [I18nErrorCodes.UNEXPECTED_RETURN_TYPE]: "Unexpected return type in composer",
    [I18nErrorCodes.INVALID_ARGUMENT]: "Invalid argument",
    [I18nErrorCodes.MUST_BE_CALL_SETUP_TOP]: "Must be called at the top of a `setup` function",
    [I18nErrorCodes.NOT_INSTALLED]: "Need to install with `app.use` function",
    [I18nErrorCodes.UNEXPECTED_ERROR]: "Unexpected error",
    [I18nErrorCodes.NOT_AVAILABLE_IN_LEGACY_MODE]: "Not available in legacy mode",
    [I18nErrorCodes.REQUIRED_VALUE]: `Required in value: {0}`,
    [I18nErrorCodes.INVALID_VALUE]: `Invalid value`,
    [I18nErrorCodes.CANNOT_SETUP_VUE_DEVTOOLS_PLUGIN]: `Cannot setup vue-devtools plugin`,
    [I18nErrorCodes.NOT_INSTALLED_WITH_PROVIDE]: "Need to install with `provide` function",
    [I18nErrorCodes.NOT_COMPATIBLE_LEGACY_VUE_I18N]: "Not compatible legacy VueI18n.",
    [I18nErrorCodes.BRIDGE_SUPPORT_VUE_2_ONLY]: "vue-i18n-bridge support Vue 2.x only",
    [I18nErrorCodes.MUST_DEFINE_I18N_OPTION_IN_ALLOW_COMPOSITION]: "Must define ‘i18n’ option or custom block in Composition API with using local scope in Legacy API mode",
    [I18nErrorCodes.NOT_AVAILABLE_COMPOSITION_IN_LEGACY]: "Not available Compostion API in Legacy API mode. Please make sure that the legacy API mode is working properly"
  };
  const TranslateVNodeSymbol = /* @__PURE__ */ makeSymbol("__translateVNode");
  const DatetimePartsSymbol = /* @__PURE__ */ makeSymbol("__datetimeParts");
  const NumberPartsSymbol = /* @__PURE__ */ makeSymbol("__numberParts");
  const EnableEmitter = /* @__PURE__ */ makeSymbol("__enableEmitter");
  const DisableEmitter = /* @__PURE__ */ makeSymbol("__disableEmitter");
  const SetPluralRulesSymbol = makeSymbol("__setPluralRules");
  const InejctWithOptionSymbol = /* @__PURE__ */ makeSymbol("__injectWithOption");
  const DisposeSymbol = /* @__PURE__ */ makeSymbol("__dispose");
  function handleFlatJson(obj) {
    if (!isObject$1(obj)) {
      return obj;
    }
    for (const key in obj) {
      if (!hasOwn(obj, key)) {
        continue;
      }
      if (!key.includes(".")) {
        if (isObject$1(obj[key])) {
          handleFlatJson(obj[key]);
        }
      } else {
        const subKeys = key.split(".");
        const lastIndex = subKeys.length - 1;
        let currentObj = obj;
        let hasStringValue = false;
        for (let i = 0; i < lastIndex; i++) {
          if (!(subKeys[i] in currentObj)) {
            currentObj[subKeys[i]] = {};
          }
          if (!isObject$1(currentObj[subKeys[i]])) {
            ({}).NODE_ENV !== "production" && warn(getWarnMessage(I18nWarnCodes.IGNORE_OBJ_FLATTEN, {
              key: subKeys[i]
            }));
            hasStringValue = true;
            break;
          }
          currentObj = currentObj[subKeys[i]];
        }
        if (!hasStringValue) {
          currentObj[subKeys[lastIndex]] = obj[key];
          delete obj[key];
        }
        if (isObject$1(currentObj[subKeys[lastIndex]])) {
          handleFlatJson(currentObj[subKeys[lastIndex]]);
        }
      }
    }
    return obj;
  }
  function getLocaleMessages(locale, options) {
    const { messages, __i18n, messageResolver, flatJson } = options;
    const ret = isPlainObject(messages) ? messages : isArray(__i18n) ? {} : { [locale]: {} };
    if (isArray(__i18n)) {
      __i18n.forEach((custom) => {
        if ("locale" in custom && "resource" in custom) {
          const { locale: locale2, resource } = custom;
          if (locale2) {
            ret[locale2] = ret[locale2] || {};
            deepCopy(resource, ret[locale2]);
          } else {
            deepCopy(resource, ret);
          }
        } else {
          isString$1(custom) && deepCopy(JSON.parse(custom), ret);
        }
      });
    }
    if (messageResolver == null && flatJson) {
      for (const key in ret) {
        if (hasOwn(ret, key)) {
          handleFlatJson(ret[key]);
        }
      }
    }
    return ret;
  }
  const isNotObjectOrIsArray = (val) => !isObject$1(val) || isArray(val);
  function deepCopy(src, des) {
    if (isNotObjectOrIsArray(src) || isNotObjectOrIsArray(des)) {
      throw createI18nError(I18nErrorCodes.INVALID_VALUE);
    }
    for (const key in src) {
      if (hasOwn(src, key)) {
        if (isNotObjectOrIsArray(src[key]) || isNotObjectOrIsArray(des[key])) {
          des[key] = src[key];
        } else {
          deepCopy(src[key], des[key]);
        }
      }
    }
  }
  function getComponentOptions(instance) {
    return instance.type;
  }
  function adjustI18nResources(gl, options, componentOptions) {
    let messages = isObject$1(options.messages) ? options.messages : {};
    if ("__i18nGlobal" in componentOptions) {
      messages = getLocaleMessages(gl.locale.value, {
        messages,
        __i18n: componentOptions.__i18nGlobal
      });
    }
    const locales = Object.keys(messages);
    if (locales.length) {
      locales.forEach((locale) => {
        gl.mergeLocaleMessage(locale, messages[locale]);
      });
    }
    {
      if (isObject$1(options.datetimeFormats)) {
        const locales2 = Object.keys(options.datetimeFormats);
        if (locales2.length) {
          locales2.forEach((locale) => {
            gl.mergeDateTimeFormat(locale, options.datetimeFormats[locale]);
          });
        }
      }
      if (isObject$1(options.numberFormats)) {
        const locales2 = Object.keys(options.numberFormats);
        if (locales2.length) {
          locales2.forEach((locale) => {
            gl.mergeNumberFormat(locale, options.numberFormats[locale]);
          });
        }
      }
    }
  }
  function createTextNode(key) {
    return vue.createVNode(vue.Text, null, key, 0);
  }
  const DEVTOOLS_META = "__INTLIFY_META__";
  let composerID = 0;
  function defineCoreMissingHandler(missing) {
    return (ctx, locale, key, type) => {
      return missing(locale, key, vue.getCurrentInstance() || void 0, type);
    };
  }
  const getMetaInfo = () => {
    const instance = vue.getCurrentInstance();
    let meta = null;
    return instance && (meta = getComponentOptions(instance)[DEVTOOLS_META]) ? { [DEVTOOLS_META]: meta } : null;
  };
  function createComposer(options = {}, VueI18nLegacy) {
    const { __root, __injectWithOption } = options;
    const _isGlobal = __root === void 0;
    let _inheritLocale = isBoolean(options.inheritLocale) ? options.inheritLocale : true;
    const _locale = vue.ref(
      // prettier-ignore
      __root && _inheritLocale ? __root.locale.value : isString$1(options.locale) ? options.locale : DEFAULT_LOCALE
    );
    const _fallbackLocale = vue.ref(
      // prettier-ignore
      __root && _inheritLocale ? __root.fallbackLocale.value : isString$1(options.fallbackLocale) || isArray(options.fallbackLocale) || isPlainObject(options.fallbackLocale) || options.fallbackLocale === false ? options.fallbackLocale : _locale.value
    );
    const _messages = vue.ref(getLocaleMessages(_locale.value, options));
    const _datetimeFormats = vue.ref(isPlainObject(options.datetimeFormats) ? options.datetimeFormats : { [_locale.value]: {} });
    const _numberFormats = vue.ref(isPlainObject(options.numberFormats) ? options.numberFormats : { [_locale.value]: {} });
    let _missingWarn = __root ? __root.missingWarn : isBoolean(options.missingWarn) || isRegExp(options.missingWarn) ? options.missingWarn : true;
    let _fallbackWarn = __root ? __root.fallbackWarn : isBoolean(options.fallbackWarn) || isRegExp(options.fallbackWarn) ? options.fallbackWarn : true;
    let _fallbackRoot = __root ? __root.fallbackRoot : isBoolean(options.fallbackRoot) ? options.fallbackRoot : true;
    let _fallbackFormat = !!options.fallbackFormat;
    let _missing = isFunction(options.missing) ? options.missing : null;
    let _runtimeMissing = isFunction(options.missing) ? defineCoreMissingHandler(options.missing) : null;
    let _postTranslation = isFunction(options.postTranslation) ? options.postTranslation : null;
    let _warnHtmlMessage = __root ? __root.warnHtmlMessage : isBoolean(options.warnHtmlMessage) ? options.warnHtmlMessage : true;
    let _escapeParameter = !!options.escapeParameter;
    const _modifiers = __root ? __root.modifiers : isPlainObject(options.modifiers) ? options.modifiers : {};
    let _pluralRules = options.pluralRules || __root && __root.pluralRules;
    let _context;
    const getCoreContext = () => {
      _isGlobal && setFallbackContext(null);
      const ctxOptions = {
        version: VERSION,
        locale: _locale.value,
        fallbackLocale: _fallbackLocale.value,
        messages: _messages.value,
        modifiers: _modifiers,
        pluralRules: _pluralRules,
        missing: _runtimeMissing === null ? void 0 : _runtimeMissing,
        missingWarn: _missingWarn,
        fallbackWarn: _fallbackWarn,
        fallbackFormat: _fallbackFormat,
        unresolving: true,
        postTranslation: _postTranslation === null ? void 0 : _postTranslation,
        warnHtmlMessage: _warnHtmlMessage,
        escapeParameter: _escapeParameter,
        messageResolver: options.messageResolver,
        messageCompiler: options.messageCompiler,
        __meta: { framework: "vue" }
      };
      {
        ctxOptions.datetimeFormats = _datetimeFormats.value;
        ctxOptions.numberFormats = _numberFormats.value;
        ctxOptions.__datetimeFormatters = isPlainObject(_context) ? _context.__datetimeFormatters : void 0;
        ctxOptions.__numberFormatters = isPlainObject(_context) ? _context.__numberFormatters : void 0;
      }
      if ({}.NODE_ENV !== "production") {
        ctxOptions.__v_emitter = isPlainObject(_context) ? _context.__v_emitter : void 0;
      }
      const ctx = createCoreContext(ctxOptions);
      _isGlobal && setFallbackContext(ctx);
      return ctx;
    };
    _context = getCoreContext();
    updateFallbackLocale(_context, _locale.value, _fallbackLocale.value);
    function trackReactivityValues() {
      return [
        _locale.value,
        _fallbackLocale.value,
        _messages.value,
        _datetimeFormats.value,
        _numberFormats.value
      ];
    }
    const locale = vue.computed({
      get: () => _locale.value,
      set: (val) => {
        _locale.value = val;
        _context.locale = _locale.value;
      }
    });
    const fallbackLocale = vue.computed({
      get: () => _fallbackLocale.value,
      set: (val) => {
        _fallbackLocale.value = val;
        _context.fallbackLocale = _fallbackLocale.value;
        updateFallbackLocale(_context, _locale.value, val);
      }
    });
    const messages = vue.computed(() => _messages.value);
    const datetimeFormats = /* @__PURE__ */ vue.computed(() => _datetimeFormats.value);
    const numberFormats = /* @__PURE__ */ vue.computed(() => _numberFormats.value);
    function getPostTranslationHandler() {
      return isFunction(_postTranslation) ? _postTranslation : null;
    }
    function setPostTranslationHandler(handler) {
      _postTranslation = handler;
      _context.postTranslation = handler;
    }
    function getMissingHandler() {
      return _missing;
    }
    function setMissingHandler(handler) {
      if (handler !== null) {
        _runtimeMissing = defineCoreMissingHandler(handler);
      }
      _missing = handler;
      _context.missing = _runtimeMissing;
    }
    function isResolvedTranslateMessage(type, arg) {
      return type !== "translate" || !arg.resolvedMessage;
    }
    const wrapWithDeps = (fn, argumentParser, warnType, fallbackSuccess, fallbackFail, successCondition) => {
      trackReactivityValues();
      let ret;
      try {
        if ({}.NODE_ENV !== "production" || __INTLIFY_PROD_DEVTOOLS__) {
          setAdditionalMeta(getMetaInfo());
        }
        if (!_isGlobal) {
          _context.fallbackContext = __root ? getFallbackContext() : void 0;
        }
        ret = fn(_context);
      } finally {
        if ({}.NODE_ENV !== "production" || __INTLIFY_PROD_DEVTOOLS__) {
          setAdditionalMeta(null);
        }
        if (!_isGlobal) {
          _context.fallbackContext = void 0;
        }
      }
      if (isNumber(ret) && ret === NOT_REOSLVED) {
        const [key, arg2] = argumentParser();
        if ({}.NODE_ENV !== "production" && __root && isString$1(key) && isResolvedTranslateMessage(warnType, arg2)) {
          if (_fallbackRoot && (isTranslateFallbackWarn(_fallbackWarn, key) || isTranslateMissingWarn(_missingWarn, key))) {
            warn(getWarnMessage(I18nWarnCodes.FALLBACK_TO_ROOT, {
              key,
              type: warnType
            }));
          }
          if ({}.NODE_ENV !== "production") {
            const { __v_emitter: emitter } = _context;
            if (emitter && _fallbackRoot) {
              emitter.emit("fallback", {
                type: warnType,
                key,
                to: "global",
                groupId: `${warnType}:${key}`
              });
            }
          }
        }
        return __root && _fallbackRoot ? fallbackSuccess(__root) : fallbackFail(key);
      } else if (successCondition(ret)) {
        return ret;
      } else {
        throw createI18nError(I18nErrorCodes.UNEXPECTED_RETURN_TYPE);
      }
    };
    function t2(...args) {
      return wrapWithDeps((context) => Reflect.apply(translate, null, [context, ...args]), () => parseTranslateArgs(...args), "translate", (root) => Reflect.apply(root.t, root, [...args]), (key) => key, (val) => isString$1(val));
    }
    function rt2(...args) {
      const [arg1, arg2, arg3] = args;
      if (arg3 && !isObject$1(arg3)) {
        throw createI18nError(I18nErrorCodes.INVALID_ARGUMENT);
      }
      return t2(...[arg1, arg2, assign$1({ resolvedMessage: true }, arg3 || {})]);
    }
    function d(...args) {
      return wrapWithDeps((context) => Reflect.apply(datetime, null, [context, ...args]), () => parseDateTimeArgs(...args), "datetime format", (root) => Reflect.apply(root.d, root, [...args]), () => MISSING_RESOLVE_VALUE, (val) => isString$1(val));
    }
    function n(...args) {
      return wrapWithDeps((context) => Reflect.apply(number, null, [context, ...args]), () => parseNumberArgs(...args), "number format", (root) => Reflect.apply(root.n, root, [...args]), () => MISSING_RESOLVE_VALUE, (val) => isString$1(val));
    }
    function normalize(values) {
      return values.map((val) => isString$1(val) || isNumber(val) || isBoolean(val) ? createTextNode(String(val)) : val);
    }
    const interpolate = (val) => val;
    const processor = {
      normalize,
      interpolate,
      type: "vnode"
    };
    function translateVNode(...args) {
      return wrapWithDeps(
        (context) => {
          let ret;
          const _context2 = context;
          try {
            _context2.processor = processor;
            ret = Reflect.apply(translate, null, [_context2, ...args]);
          } finally {
            _context2.processor = null;
          }
          return ret;
        },
        () => parseTranslateArgs(...args),
        "translate",
        // eslint-disable-next-line @typescript-eslint/no-explicit-any
        (root) => root[TranslateVNodeSymbol](...args),
        (key) => [createTextNode(key)],
        (val) => isArray(val)
      );
    }
    function numberParts(...args) {
      return wrapWithDeps(
        (context) => Reflect.apply(number, null, [context, ...args]),
        () => parseNumberArgs(...args),
        "number format",
        // eslint-disable-next-line @typescript-eslint/no-explicit-any
        (root) => root[NumberPartsSymbol](...args),
        () => [],
        (val) => isString$1(val) || isArray(val)
      );
    }
    function datetimeParts(...args) {
      return wrapWithDeps(
        (context) => Reflect.apply(datetime, null, [context, ...args]),
        () => parseDateTimeArgs(...args),
        "datetime format",
        // eslint-disable-next-line @typescript-eslint/no-explicit-any
        (root) => root[DatetimePartsSymbol](...args),
        () => [],
        (val) => isString$1(val) || isArray(val)
      );
    }
    function setPluralRules(rules) {
      _pluralRules = rules;
      _context.pluralRules = _pluralRules;
    }
    function te2(key, locale2) {
      if (!key)
        return false;
      const targetLocale = isString$1(locale2) ? locale2 : _locale.value;
      const message = getLocaleMessage(targetLocale);
      return _context.messageResolver(message, key) !== null;
    }
    function resolveMessages(key) {
      let messages2 = null;
      const locales = fallbackWithLocaleChain(_context, _fallbackLocale.value, _locale.value);
      for (let i = 0; i < locales.length; i++) {
        const targetLocaleMessages = _messages.value[locales[i]] || {};
        const messageValue = _context.messageResolver(targetLocaleMessages, key);
        if (messageValue != null) {
          messages2 = messageValue;
          break;
        }
      }
      return messages2;
    }
    function tm(key) {
      const messages2 = resolveMessages(key);
      return messages2 != null ? messages2 : __root ? __root.tm(key) || {} : {};
    }
    function getLocaleMessage(locale2) {
      return _messages.value[locale2] || {};
    }
    function setLocaleMessage(locale2, message) {
      _messages.value[locale2] = message;
      _context.messages = _messages.value;
    }
    function mergeLocaleMessage(locale2, message) {
      _messages.value[locale2] = _messages.value[locale2] || {};
      deepCopy(message, _messages.value[locale2]);
      _context.messages = _messages.value;
    }
    function getDateTimeFormat(locale2) {
      return _datetimeFormats.value[locale2] || {};
    }
    function setDateTimeFormat(locale2, format2) {
      _datetimeFormats.value[locale2] = format2;
      _context.datetimeFormats = _datetimeFormats.value;
      clearDateTimeFormat(_context, locale2, format2);
    }
    function mergeDateTimeFormat(locale2, format2) {
      _datetimeFormats.value[locale2] = assign$1(_datetimeFormats.value[locale2] || {}, format2);
      _context.datetimeFormats = _datetimeFormats.value;
      clearDateTimeFormat(_context, locale2, format2);
    }
    function getNumberFormat(locale2) {
      return _numberFormats.value[locale2] || {};
    }
    function setNumberFormat(locale2, format2) {
      _numberFormats.value[locale2] = format2;
      _context.numberFormats = _numberFormats.value;
      clearNumberFormat(_context, locale2, format2);
    }
    function mergeNumberFormat(locale2, format2) {
      _numberFormats.value[locale2] = assign$1(_numberFormats.value[locale2] || {}, format2);
      _context.numberFormats = _numberFormats.value;
      clearNumberFormat(_context, locale2, format2);
    }
    composerID++;
    if (__root && inBrowser) {
      vue.watch(__root.locale, (val) => {
        if (_inheritLocale) {
          _locale.value = val;
          _context.locale = val;
          updateFallbackLocale(_context, _locale.value, _fallbackLocale.value);
        }
      });
      vue.watch(__root.fallbackLocale, (val) => {
        if (_inheritLocale) {
          _fallbackLocale.value = val;
          _context.fallbackLocale = val;
          updateFallbackLocale(_context, _locale.value, _fallbackLocale.value);
        }
      });
    }
    const composer = {
      id: composerID,
      locale,
      fallbackLocale,
      get inheritLocale() {
        return _inheritLocale;
      },
      set inheritLocale(val) {
        _inheritLocale = val;
        if (val && __root) {
          _locale.value = __root.locale.value;
          _fallbackLocale.value = __root.fallbackLocale.value;
          updateFallbackLocale(_context, _locale.value, _fallbackLocale.value);
        }
      },
      get availableLocales() {
        return Object.keys(_messages.value).sort();
      },
      messages,
      get modifiers() {
        return _modifiers;
      },
      get pluralRules() {
        return _pluralRules || {};
      },
      get isGlobal() {
        return _isGlobal;
      },
      get missingWarn() {
        return _missingWarn;
      },
      set missingWarn(val) {
        _missingWarn = val;
        _context.missingWarn = _missingWarn;
      },
      get fallbackWarn() {
        return _fallbackWarn;
      },
      set fallbackWarn(val) {
        _fallbackWarn = val;
        _context.fallbackWarn = _fallbackWarn;
      },
      get fallbackRoot() {
        return _fallbackRoot;
      },
      set fallbackRoot(val) {
        _fallbackRoot = val;
      },
      get fallbackFormat() {
        return _fallbackFormat;
      },
      set fallbackFormat(val) {
        _fallbackFormat = val;
        _context.fallbackFormat = _fallbackFormat;
      },
      get warnHtmlMessage() {
        return _warnHtmlMessage;
      },
      set warnHtmlMessage(val) {
        _warnHtmlMessage = val;
        _context.warnHtmlMessage = val;
      },
      get escapeParameter() {
        return _escapeParameter;
      },
      set escapeParameter(val) {
        _escapeParameter = val;
        _context.escapeParameter = val;
      },
      t: t2,
      getLocaleMessage,
      setLocaleMessage,
      mergeLocaleMessage,
      getPostTranslationHandler,
      setPostTranslationHandler,
      getMissingHandler,
      setMissingHandler,
      [SetPluralRulesSymbol]: setPluralRules
    };
    {
      composer.datetimeFormats = datetimeFormats;
      composer.numberFormats = numberFormats;
      composer.rt = rt2;
      composer.te = te2;
      composer.tm = tm;
      composer.d = d;
      composer.n = n;
      composer.getDateTimeFormat = getDateTimeFormat;
      composer.setDateTimeFormat = setDateTimeFormat;
      composer.mergeDateTimeFormat = mergeDateTimeFormat;
      composer.getNumberFormat = getNumberFormat;
      composer.setNumberFormat = setNumberFormat;
      composer.mergeNumberFormat = mergeNumberFormat;
      composer[InejctWithOptionSymbol] = __injectWithOption;
      composer[TranslateVNodeSymbol] = translateVNode;
      composer[DatetimePartsSymbol] = datetimeParts;
      composer[NumberPartsSymbol] = numberParts;
    }
    if ({}.NODE_ENV !== "production") {
      composer[EnableEmitter] = (emitter) => {
        _context.__v_emitter = emitter;
      };
      composer[DisableEmitter] = () => {
        _context.__v_emitter = void 0;
      };
    }
    return composer;
  }
  const baseFormatProps = {
    tag: {
      type: [String, Object]
    },
    locale: {
      type: String
    },
    scope: {
      type: String,
      // NOTE: avoid https://github.com/microsoft/rushstack/issues/1050
      validator: (val) => val === "parent" || val === "global",
      default: "parent"
      /* ComponentI18nScope */
    },
    i18n: {
      type: Object
    }
  };
  function getInterpolateArg({ slots }, keys) {
    if (keys.length === 1 && keys[0] === "default") {
      const ret = slots.default ? slots.default() : [];
      return ret.reduce((slot, current) => {
        return [
          ...slot,
          // prettier-ignore
          ...current.type === vue.Fragment ? current.children : [current]
        ];
      }, []);
    } else {
      return keys.reduce((arg, key) => {
        const slot = slots[key];
        if (slot) {
          arg[key] = slot();
        }
        return arg;
      }, {});
    }
  }
  function getFragmentableTag(tag) {
    return vue.Fragment;
  }
  /* @__PURE__ */ vue.defineComponent({
    /* eslint-disable */
    name: "i18n-t",
    props: assign$1({
      keypath: {
        type: String,
        required: true
      },
      plural: {
        type: [Number, String],
        // eslint-disable-next-line @typescript-eslint/no-explicit-any
        validator: (val) => isNumber(val) || !isNaN(val)
      }
    }, baseFormatProps),
    /* eslint-enable */
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    setup(props, context) {
      const { slots, attrs } = context;
      const i18n = props.i18n || useI18n({
        useScope: props.scope,
        __useComponent: true
      });
      return () => {
        const keys = Object.keys(slots).filter((key) => key !== "_");
        const options = {};
        if (props.locale) {
          options.locale = props.locale;
        }
        if (props.plural !== void 0) {
          options.plural = isString$1(props.plural) ? +props.plural : props.plural;
        }
        const arg = getInterpolateArg(context, keys);
        const children = i18n[TranslateVNodeSymbol](props.keypath, arg, options);
        const assignedAttrs = assign$1({}, attrs);
        const tag = isString$1(props.tag) || isObject$1(props.tag) ? props.tag : getFragmentableTag();
        return vue.h(tag, assignedAttrs, children);
      };
    }
  });
  function isVNode(target) {
    return isArray(target) && !isString$1(target[0]);
  }
  function renderFormatter(props, context, slotKeys, partFormatter) {
    const { slots, attrs } = context;
    return () => {
      const options = { part: true };
      let overrides = {};
      if (props.locale) {
        options.locale = props.locale;
      }
      if (isString$1(props.format)) {
        options.key = props.format;
      } else if (isObject$1(props.format)) {
        if (isString$1(props.format.key)) {
          options.key = props.format.key;
        }
        overrides = Object.keys(props.format).reduce((options2, prop) => {
          return slotKeys.includes(prop) ? assign$1({}, options2, { [prop]: props.format[prop] }) : options2;
        }, {});
      }
      const parts = partFormatter(...[props.value, options, overrides]);
      let children = [options.key];
      if (isArray(parts)) {
        children = parts.map((part, index) => {
          const slot = slots[part.type];
          const node = slot ? slot({ [part.type]: part.value, index, parts }) : [part.value];
          if (isVNode(node)) {
            node[0].key = `${part.type}-${index}`;
          }
          return node;
        });
      } else if (isString$1(parts)) {
        children = [parts];
      }
      const assignedAttrs = assign$1({}, attrs);
      const tag = isString$1(props.tag) || isObject$1(props.tag) ? props.tag : getFragmentableTag();
      return vue.h(tag, assignedAttrs, children);
    };
  }
  /* @__PURE__ */ vue.defineComponent({
    /* eslint-disable */
    name: "i18n-n",
    props: assign$1({
      value: {
        type: Number,
        required: true
      },
      format: {
        type: [String, Object]
      }
    }, baseFormatProps),
    /* eslint-enable */
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    setup(props, context) {
      const i18n = props.i18n || useI18n({
        useScope: "parent",
        __useComponent: true
      });
      return renderFormatter(props, context, NUMBER_FORMAT_OPTIONS_KEYS, (...args) => (
        // eslint-disable-next-line @typescript-eslint/no-explicit-any
        i18n[NumberPartsSymbol](...args)
      ));
    }
  });
  /* @__PURE__ */ vue.defineComponent({
    /* eslint-disable */
    name: "i18n-d",
    props: assign$1({
      value: {
        type: [Number, Date],
        required: true
      },
      format: {
        type: [String, Object]
      }
    }, baseFormatProps),
    /* eslint-enable */
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    setup(props, context) {
      const i18n = props.i18n || useI18n({
        useScope: "parent",
        __useComponent: true
      });
      return renderFormatter(props, context, DATETIME_FORMAT_OPTIONS_KEYS, (...args) => (
        // eslint-disable-next-line @typescript-eslint/no-explicit-any
        i18n[DatetimePartsSymbol](...args)
      ));
    }
  });
  function addTimelineEvent(event, payload) {
  }
  const I18nInjectionKey = /* @__PURE__ */ makeSymbol("global-vue-i18n");
  function useI18n(options = {}) {
    const instance = vue.getCurrentInstance();
    if (instance == null) {
      throw createI18nError(I18nErrorCodes.MUST_BE_CALL_SETUP_TOP);
    }
    if (!instance.isCE && instance.appContext.app != null && !instance.appContext.app.__VUE_I18N_SYMBOL__) {
      throw createI18nError(I18nErrorCodes.NOT_INSTALLED);
    }
    const i18n = getI18nInstance(instance);
    const gl = getGlobalComposer(i18n);
    const componentOptions = getComponentOptions(instance);
    const scope = getScope(options, componentOptions);
    if (__VUE_I18N_LEGACY_API__) {
      if (i18n.mode === "legacy" && !options.__useComponent) {
        if (!i18n.allowComposition) {
          throw createI18nError(I18nErrorCodes.NOT_AVAILABLE_IN_LEGACY_MODE);
        }
        return useI18nForLegacy(instance, scope, gl, options);
      }
    }
    if (scope === "global") {
      adjustI18nResources(gl, options, componentOptions);
      return gl;
    }
    if (scope === "parent") {
      let composer2 = getComposer(i18n, instance, options.__useComponent);
      if (composer2 == null) {
        if ({}.NODE_ENV !== "production") {
          warn(getWarnMessage(I18nWarnCodes.NOT_FOUND_PARENT_SCOPE));
        }
        composer2 = gl;
      }
      return composer2;
    }
    const i18nInternal = i18n;
    let composer = i18nInternal.__getInstance(instance);
    if (composer == null) {
      const composerOptions = assign$1({}, options);
      if ("__i18n" in componentOptions) {
        composerOptions.__i18n = componentOptions.__i18n;
      }
      if (gl) {
        composerOptions.__root = gl;
      }
      composer = createComposer(composerOptions);
      if (i18nInternal.__composerExtend) {
        composer[DisposeSymbol] = i18nInternal.__composerExtend(composer);
      }
      setupLifeCycle(i18nInternal, instance, composer);
      i18nInternal.__setInstance(instance, composer);
    }
    return composer;
  }
  function getI18nInstance(instance) {
    {
      const i18n = vue.inject(!instance.isCE ? instance.appContext.app.__VUE_I18N_SYMBOL__ : I18nInjectionKey);
      if (!i18n) {
        throw createI18nError(!instance.isCE ? I18nErrorCodes.UNEXPECTED_ERROR : I18nErrorCodes.NOT_INSTALLED_WITH_PROVIDE);
      }
      return i18n;
    }
  }
  function getScope(options, componentOptions) {
    return isEmptyObject(options) ? "__i18n" in componentOptions ? "local" : "global" : !options.useScope ? "local" : options.useScope;
  }
  function getGlobalComposer(i18n) {
    return i18n.mode === "composition" ? i18n.global : i18n.global.__composer;
  }
  function getComposer(i18n, target, useComponent = false) {
    let composer = null;
    const root = target.root;
    let current = getParentComponentInstance(target, useComponent);
    while (current != null) {
      const i18nInternal = i18n;
      if (i18n.mode === "composition") {
        composer = i18nInternal.__getInstance(current);
      } else {
        if (__VUE_I18N_LEGACY_API__) {
          const vueI18n = i18nInternal.__getInstance(current);
          if (vueI18n != null) {
            composer = vueI18n.__composer;
            if (useComponent && composer && !composer[InejctWithOptionSymbol]) {
              composer = null;
            }
          }
        }
      }
      if (composer != null) {
        break;
      }
      if (root === current) {
        break;
      }
      current = current.parent;
    }
    return composer;
  }
  function getParentComponentInstance(target, useComponent = false) {
    if (target == null) {
      return null;
    }
    {
      return !useComponent ? target.parent : target.vnode.ctx || target.parent;
    }
  }
  function setupLifeCycle(i18n, target, composer) {
    let emitter = null;
    {
      vue.onMounted(() => {
        if (({}.NODE_ENV !== "production" || false) && true && target.vnode.el) {
          target.vnode.el.__VUE_I18N__ = composer;
          emitter = createEmitter();
          const _composer = composer;
          _composer[EnableEmitter] && _composer[EnableEmitter](emitter);
          emitter.on("*", addTimelineEvent);
        }
      }, target);
      vue.onUnmounted(() => {
        const _composer = composer;
        if (({}.NODE_ENV !== "production" || false) && true && target.vnode.el && target.vnode.el.__VUE_I18N__) {
          emitter && emitter.off("*", addTimelineEvent);
          _composer[DisableEmitter] && _composer[DisableEmitter]();
          delete target.vnode.el.__VUE_I18N__;
        }
        i18n.__deleteInstance(target);
        const dispose = _composer[DisposeSymbol];
        if (dispose) {
          dispose();
          delete _composer[DisposeSymbol];
        }
      }, target);
    }
  }
  function useI18nForLegacy(instance, scope, root, options = {}) {
    const isLocalScope = scope === "local";
    const _composer = vue.shallowRef(null);
    if (isLocalScope && instance.proxy && !(instance.proxy.$options.i18n || instance.proxy.$options.__i18n)) {
      throw createI18nError(I18nErrorCodes.MUST_DEFINE_I18N_OPTION_IN_ALLOW_COMPOSITION);
    }
    const _inheritLocale = isBoolean(options.inheritLocale) ? options.inheritLocale : !isString$1(options.locale);
    const _locale = vue.ref(
      // prettier-ignore
      !isLocalScope || _inheritLocale ? root.locale.value : isString$1(options.locale) ? options.locale : DEFAULT_LOCALE
    );
    const _fallbackLocale = vue.ref(
      // prettier-ignore
      !isLocalScope || _inheritLocale ? root.fallbackLocale.value : isString$1(options.fallbackLocale) || isArray(options.fallbackLocale) || isPlainObject(options.fallbackLocale) || options.fallbackLocale === false ? options.fallbackLocale : _locale.value
    );
    const _messages = vue.ref(getLocaleMessages(_locale.value, options));
    const _datetimeFormats = vue.ref(isPlainObject(options.datetimeFormats) ? options.datetimeFormats : { [_locale.value]: {} });
    const _numberFormats = vue.ref(isPlainObject(options.numberFormats) ? options.numberFormats : { [_locale.value]: {} });
    const _missingWarn = isLocalScope ? root.missingWarn : isBoolean(options.missingWarn) || isRegExp(options.missingWarn) ? options.missingWarn : true;
    const _fallbackWarn = isLocalScope ? root.fallbackWarn : isBoolean(options.fallbackWarn) || isRegExp(options.fallbackWarn) ? options.fallbackWarn : true;
    const _fallbackRoot = isLocalScope ? root.fallbackRoot : isBoolean(options.fallbackRoot) ? options.fallbackRoot : true;
    const _fallbackFormat = !!options.fallbackFormat;
    const _missing = isFunction(options.missing) ? options.missing : null;
    const _postTranslation = isFunction(options.postTranslation) ? options.postTranslation : null;
    const _warnHtmlMessage = isLocalScope ? root.warnHtmlMessage : isBoolean(options.warnHtmlMessage) ? options.warnHtmlMessage : true;
    const _escapeParameter = !!options.escapeParameter;
    const _modifiers = isLocalScope ? root.modifiers : isPlainObject(options.modifiers) ? options.modifiers : {};
    const _pluralRules = options.pluralRules || isLocalScope && root.pluralRules;
    function trackReactivityValues() {
      return [
        _locale.value,
        _fallbackLocale.value,
        _messages.value,
        _datetimeFormats.value,
        _numberFormats.value
      ];
    }
    const locale = vue.computed({
      get: () => {
        return _composer.value ? _composer.value.locale.value : _locale.value;
      },
      set: (val) => {
        if (_composer.value) {
          _composer.value.locale.value = val;
        }
        _locale.value = val;
      }
    });
    const fallbackLocale = vue.computed({
      get: () => {
        return _composer.value ? _composer.value.fallbackLocale.value : _fallbackLocale.value;
      },
      set: (val) => {
        if (_composer.value) {
          _composer.value.fallbackLocale.value = val;
        }
        _fallbackLocale.value = val;
      }
    });
    const messages = vue.computed(() => {
      if (_composer.value) {
        return _composer.value.messages.value;
      } else {
        return _messages.value;
      }
    });
    const datetimeFormats = vue.computed(() => _datetimeFormats.value);
    const numberFormats = vue.computed(() => _numberFormats.value);
    function getPostTranslationHandler() {
      return _composer.value ? _composer.value.getPostTranslationHandler() : _postTranslation;
    }
    function setPostTranslationHandler(handler) {
      if (_composer.value) {
        _composer.value.setPostTranslationHandler(handler);
      }
    }
    function getMissingHandler() {
      return _composer.value ? _composer.value.getMissingHandler() : _missing;
    }
    function setMissingHandler(handler) {
      if (_composer.value) {
        _composer.value.setMissingHandler(handler);
      }
    }
    function warpWithDeps(fn) {
      trackReactivityValues();
      return fn();
    }
    function t2(...args) {
      return _composer.value ? warpWithDeps(() => Reflect.apply(_composer.value.t, null, [...args])) : warpWithDeps(() => "");
    }
    function rt2(...args) {
      return _composer.value ? Reflect.apply(_composer.value.rt, null, [...args]) : "";
    }
    function d(...args) {
      return _composer.value ? warpWithDeps(() => Reflect.apply(_composer.value.d, null, [...args])) : warpWithDeps(() => "");
    }
    function n(...args) {
      return _composer.value ? warpWithDeps(() => Reflect.apply(_composer.value.n, null, [...args])) : warpWithDeps(() => "");
    }
    function tm(key) {
      return _composer.value ? _composer.value.tm(key) : {};
    }
    function te2(key, locale2) {
      return _composer.value ? _composer.value.te(key, locale2) : false;
    }
    function getLocaleMessage(locale2) {
      return _composer.value ? _composer.value.getLocaleMessage(locale2) : {};
    }
    function setLocaleMessage(locale2, message) {
      if (_composer.value) {
        _composer.value.setLocaleMessage(locale2, message);
        _messages.value[locale2] = message;
      }
    }
    function mergeLocaleMessage(locale2, message) {
      if (_composer.value) {
        _composer.value.mergeLocaleMessage(locale2, message);
      }
    }
    function getDateTimeFormat(locale2) {
      return _composer.value ? _composer.value.getDateTimeFormat(locale2) : {};
    }
    function setDateTimeFormat(locale2, format2) {
      if (_composer.value) {
        _composer.value.setDateTimeFormat(locale2, format2);
        _datetimeFormats.value[locale2] = format2;
      }
    }
    function mergeDateTimeFormat(locale2, format2) {
      if (_composer.value) {
        _composer.value.mergeDateTimeFormat(locale2, format2);
      }
    }
    function getNumberFormat(locale2) {
      return _composer.value ? _composer.value.getNumberFormat(locale2) : {};
    }
    function setNumberFormat(locale2, format2) {
      if (_composer.value) {
        _composer.value.setNumberFormat(locale2, format2);
        _numberFormats.value[locale2] = format2;
      }
    }
    function mergeNumberFormat(locale2, format2) {
      if (_composer.value) {
        _composer.value.mergeNumberFormat(locale2, format2);
      }
    }
    const wrapper = {
      get id() {
        return _composer.value ? _composer.value.id : -1;
      },
      locale,
      fallbackLocale,
      messages,
      datetimeFormats,
      numberFormats,
      get inheritLocale() {
        return _composer.value ? _composer.value.inheritLocale : _inheritLocale;
      },
      set inheritLocale(val) {
        if (_composer.value) {
          _composer.value.inheritLocale = val;
        }
      },
      get availableLocales() {
        return _composer.value ? _composer.value.availableLocales : Object.keys(_messages.value);
      },
      get modifiers() {
        return _composer.value ? _composer.value.modifiers : _modifiers;
      },
      get pluralRules() {
        return _composer.value ? _composer.value.pluralRules : _pluralRules;
      },
      get isGlobal() {
        return _composer.value ? _composer.value.isGlobal : false;
      },
      get missingWarn() {
        return _composer.value ? _composer.value.missingWarn : _missingWarn;
      },
      set missingWarn(val) {
        if (_composer.value) {
          _composer.value.missingWarn = val;
        }
      },
      get fallbackWarn() {
        return _composer.value ? _composer.value.fallbackWarn : _fallbackWarn;
      },
      set fallbackWarn(val) {
        if (_composer.value) {
          _composer.value.missingWarn = val;
        }
      },
      get fallbackRoot() {
        return _composer.value ? _composer.value.fallbackRoot : _fallbackRoot;
      },
      set fallbackRoot(val) {
        if (_composer.value) {
          _composer.value.fallbackRoot = val;
        }
      },
      get fallbackFormat() {
        return _composer.value ? _composer.value.fallbackFormat : _fallbackFormat;
      },
      set fallbackFormat(val) {
        if (_composer.value) {
          _composer.value.fallbackFormat = val;
        }
      },
      get warnHtmlMessage() {
        return _composer.value ? _composer.value.warnHtmlMessage : _warnHtmlMessage;
      },
      set warnHtmlMessage(val) {
        if (_composer.value) {
          _composer.value.warnHtmlMessage = val;
        }
      },
      get escapeParameter() {
        return _composer.value ? _composer.value.escapeParameter : _escapeParameter;
      },
      set escapeParameter(val) {
        if (_composer.value) {
          _composer.value.escapeParameter = val;
        }
      },
      t: t2,
      getPostTranslationHandler,
      setPostTranslationHandler,
      getMissingHandler,
      setMissingHandler,
      rt: rt2,
      d,
      n,
      tm,
      te: te2,
      getLocaleMessage,
      setLocaleMessage,
      mergeLocaleMessage,
      getDateTimeFormat,
      setDateTimeFormat,
      mergeDateTimeFormat,
      getNumberFormat,
      setNumberFormat,
      mergeNumberFormat
    };
    function sync(composer) {
      composer.locale.value = _locale.value;
      composer.fallbackLocale.value = _fallbackLocale.value;
      Object.keys(_messages.value).forEach((locale2) => {
        composer.mergeLocaleMessage(locale2, _messages.value[locale2]);
      });
      Object.keys(_datetimeFormats.value).forEach((locale2) => {
        composer.mergeDateTimeFormat(locale2, _datetimeFormats.value[locale2]);
      });
      Object.keys(_numberFormats.value).forEach((locale2) => {
        composer.mergeNumberFormat(locale2, _numberFormats.value[locale2]);
      });
      composer.escapeParameter = _escapeParameter;
      composer.fallbackFormat = _fallbackFormat;
      composer.fallbackRoot = _fallbackRoot;
      composer.fallbackWarn = _fallbackWarn;
      composer.missingWarn = _missingWarn;
      composer.warnHtmlMessage = _warnHtmlMessage;
    }
    vue.onBeforeMount(() => {
      if (instance.proxy == null || instance.proxy.$i18n == null) {
        throw createI18nError(I18nErrorCodes.NOT_AVAILABLE_COMPOSITION_IN_LEGACY);
      }
      const composer = _composer.value = instance.proxy.$i18n.__composer;
      if (scope === "global") {
        _locale.value = composer.locale.value;
        _fallbackLocale.value = composer.fallbackLocale.value;
        _messages.value = composer.messages.value;
        _datetimeFormats.value = composer.datetimeFormats.value;
        _numberFormats.value = composer.numberFormats.value;
      } else if (isLocalScope) {
        sync(composer);
      }
    });
    return wrapper;
  }
  {
    initFeatureFlags();
  }
  if (__INTLIFY_JIT_COMPILATION__) {
    registerMessageCompiler(compile);
  } else {
    registerMessageCompiler(compileToFunction);
  }
  registerMessageResolver(resolveValue);
  registerLocaleFallbacker(fallbackWithLocaleChain);
  if ({}.NODE_ENV !== "production" || __INTLIFY_PROD_DEVTOOLS__) {
    const target = getGlobalThis();
    target.__INTLIFY__ = true;
    setDevToolsHook(target.__INTLIFY_DEVTOOLS_GLOBAL_HOOK__);
  }
  /*!
  * Copyright 2022, 2023 Utrecht University
  *
  * Licensed under the EUPL, Version 1.2 only
  * You may not use this work except in compliance with the
  Licence.
  * A copy of the Licence is provided in the 'LICENCE' file in this project.
  * You may also obtain a copy of the Licence at:
  *
  * https://joinup.ec.europa.eu/collection/eupl/eupl-text-eupl-12
  *
  * Unless required by applicable law or agreed to in
  writing, software distributed under the Licence is
  distributed on an "AS IS" basis,
  * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either
  express or implied.
  * See the Licence for the specific language governing
  permissions and limitations under the Licence.
  */
  function t(e) {
    return e.target.value;
  }
  /*!
  * Copyright 2022, 2023 Utrecht University
  *
  * Licensed under the EUPL, Version 1.2 only
  * You may not use this work except in compliance with the
  Licence.
  * A copy of the Licence is provided in the 'LICENCE' file in this project.
  * You may also obtain a copy of the Licence at:
  *
  * https://joinup.ec.europa.eu/collection/eupl/eupl-text-eupl-12
  *
  * Unless required by applicable law or agreed to in
  writing, software distributed under the Licence is
  distributed on an "AS IS" basis,
  * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either
  express or implied.
  * See the Licence for the specific language governing
  permissions and limitations under the Licence.
  */
  const re = ["href", "target"], ie = { class: "btn-text" }, ue = ["type", "name", "disabled"], de = { class: "btn-text" }, X = /* @__PURE__ */ vue.defineComponent({
    __name: "BSButton",
    props: {
      id: { default: null },
      href: { default: void 0 },
      name: { default: void 0 },
      variant: { default: "dark" },
      size: { default: "normal" },
      outlined: { type: Boolean, default: false },
      active: { type: Boolean, default: false },
      disabled: { type: Boolean, default: false },
      loading: { type: Boolean, default: false },
      input: { default: "button" },
      newTab: { type: Boolean, default: false },
      cssClasses: { default: "" }
    },
    setup(i) {
      const t2 = i, o = vue.computed(() => {
        let n = "btn ";
        return t2.size === "large" ? n += "btn-lg " : t2.size === "small" && (n += "btn-sm "), t2.outlined ? n += "btn-outline-" : n += "btn-", n += `${t2.variant} `, t2.loading && (n += "btn-loading "), t2.active && (n += "active "), n;
      });
      return (n, e) => n.href ? (vue.openBlock(), vue.createElementBlock("a", {
        key: 0,
        href: n.href,
        class: vue.normalizeClass(o.value),
        target: n.newTab ? "_blank" : "_self"
      }, [
        vue.createElementVNode("span", ie, [
          vue.renderSlot(n.$slots, "default")
        ])
      ], 10, re)) : (vue.openBlock(), vue.createElementBlock("button", {
        key: 1,
        type: n.input,
        class: vue.normalizeClass(o.value),
        name: n.name,
        disabled: n.disabled
      }, [
        vue.createElementVNode("span", de, [
          vue.renderSlot(n.$slots, "default")
        ])
      ], 10, ue));
    }
  });
  const Ve = ["id", "value", "checked", "onClick"], De = ["for"], Ue = /* @__PURE__ */ vue.defineComponent({
    __name: "BSMultiSelect",
    props: {
      options: {},
      modelValue: {},
      containerClasses: { default: "" },
      uniqueId: { default: v4().toString() }
    },
    emits: ["update:modelValue", "update:model-value"],
    setup(i, { emit: t2 }) {
      const o = i;
      function n(e) {
        const l = o.modelValue.includes(e);
        let a = [...o.modelValue];
        if (!l)
          a.push(e);
        else {
          const u = a.indexOf(e);
          u > -1 && a.splice(u, 1);
        }
        t2("update:modelValue", a);
      }
      return (e, l) => (vue.openBlock(), vue.createElementBlock("div", null, [
        (vue.openBlock(true), vue.createElementBlock(vue.Fragment, null, vue.renderList(e.options, ([a, u]) => (vue.openBlock(), vue.createElementBlock("div", {
          key: a,
          class: vue.normalizeClass(["form-check", e.containerClasses])
        }, [
          vue.createElementVNode("input", {
            id: "id_" + a + "_" + e.uniqueId,
            type: "checkbox",
            class: "form-check-input",
            value: a,
            checked: o.modelValue.includes(a),
            onClick: (_) => n(a)
          }, null, 8, Ve),
          vue.createElementVNode("label", {
            class: "form-check-label",
            for: +"_" + e.uniqueId
          }, vue.toDisplayString(u), 9, De)
        ], 2))), 128))
      ]));
    }
  }), Oe = {
    class: "pagination justify-content-center",
    role: "navigation",
    "aria-label": "pagination"
  }, Ie = ["onClick"], Pe = {
    key: 1,
    class: "page-link"
  }, q = /* @__PURE__ */ vue.defineComponent({
    __name: "BSPagination",
    props: {
      maxPages: {},
      currentpage: {},
      showButtons: { type: Boolean, default: true },
      numOptions: { default: 2 }
    },
    emits: ["change-page"],
    setup(i, { emit: t2 }) {
      const o = i;
      function n(u, _, b) {
        return Math.min(Math.max(u, _), b);
      }
      const e = vue.computed(() => {
        const u = o.numOptions, _ = o.currentpage - u, b = o.currentpage + u + 1, E = [], P = [];
        let D;
        for (let y = 1; y <= o.maxPages; y++)
          (y === 1 || y === o.maxPages || y >= _ && y < b) && E.push(y);
        for (const y of E)
          D && (y - D === 2 ? P.push(D + 1) : y - D !== 1 && P.push(-42)), P.push(y), D = y;
        return P;
      });
      function l(u) {
        u = n(u, 1, o.maxPages), t2("change-page", u);
      }
      const { t: a } = useI18n();
      return (u, _) => (vue.openBlock(), vue.createElementBlock("ul", Oe, [
        vue.createElementVNode("li", {
          class: vue.normalizeClass(["page-item page-button", u.currentpage === 1 ? "disabled" : ""])
        }, [
          u.showButtons ? (vue.openBlock(), vue.createElementBlock("a", {
            key: 0,
            class: "page-link",
            onClick: _[0] || (_[0] = (b) => l(u.currentpage - 1))
          }, vue.toDisplayString(vue.unref(a)("previous")), 1)) : vue.createCommentVNode("", true)
        ], 2),
        (vue.openBlock(true), vue.createElementBlock(vue.Fragment, null, vue.renderList(e.value, (b) => (vue.openBlock(), vue.createElementBlock("li", {
          key: b,
          class: vue.normalizeClass([
            "page-item",
            (b === -42 ? "disabled page-ellipsis " : "") + (b === u.currentpage ? "active" : "")
          ])
        }, [
          b !== -42 ? (vue.openBlock(), vue.createElementBlock("a", {
            key: 0,
            class: "page-link",
            onClick: (E) => l(b)
          }, vue.toDisplayString(b), 9, Ie)) : (vue.openBlock(), vue.createElementBlock("span", Pe, "…"))
        ], 2))), 128)),
        vue.createElementVNode("li", {
          class: vue.normalizeClass(["page-item page-button", u.currentpage >= u.maxPages ? "disabled" : ""])
        }, [
          u.showButtons ? (vue.openBlock(), vue.createElementBlock("a", {
            key: 0,
            class: "page-link",
            onClick: _[1] || (_[1] = (b) => l(u.currentpage + 1))
          }, vue.toDisplayString(vue.unref(a)("next")), 1)) : vue.createCommentVNode("", true)
        ], 2)
      ]));
    }
  });
  function G(i) {
    const t2 = i;
    t2.__i18n = t2.__i18n || [], t2.__i18n.push({
      locale: "",
      resource: {
        en: {
          next: (o) => {
            const { normalize: n } = o;
            return n(["Next"]);
          },
          previous: (o) => {
            const { normalize: n } = o;
            return n(["Previous"]);
          }
        },
        nl: {
          next: (o) => {
            const { normalize: n } = o;
            return n(["Volgende"]);
          },
          previous: (o) => {
            const { normalize: n } = o;
            return n(["Vorige"]);
          }
        }
      }
    });
  }
  typeof G == "function" && G(q);
  const Ee = ["id", "value", "checked", "onClick"], Le = ["for"], Ne = /* @__PURE__ */ vue.defineComponent({
    __name: "BSRadioSelect",
    props: {
      options: {},
      modelValue: {},
      containerClasses: { default: "" }
    },
    emits: ["update:modelValue", "update:model-value"],
    setup(i, { emit: t2 }) {
      return (o, n) => (vue.openBlock(), vue.createElementBlock("div", null, [
        (vue.openBlock(true), vue.createElementBlock(vue.Fragment, null, vue.renderList(o.options, ([e, l]) => (vue.openBlock(), vue.createElementBlock("div", {
          key: e,
          class: vue.normalizeClass(["form-check", o.containerClasses])
        }, [
          vue.createElementVNode("input", {
            id: "id_" + e,
            type: "radio",
            class: "form-check-input",
            value: e,
            checked: o.modelValue == e,
            onClick: (a) => t2("update:model-value", e)
          }, null, 8, Ee),
          vue.createElementVNode("label", {
            class: "form-check-label",
            for: "id_" + e
          }, vue.toDisplayString(l), 9, Le)
        ], 2))), 128))
      ]));
    }
  }), Me = { class: "uu-sidebar" }, Te = ["data-bs-target"], qe = ["id"], Re = { class: "uu-sidebar-content" }, je = /* @__PURE__ */ vue.defineComponent({
    __name: "BSSidebar",
    props: {
      id: { default: null },
      placement: { default: "left" },
      mobilePlacement: { default: "top" },
      stickySidebar: { type: Boolean, default: false },
      mobileStickySidebar: { type: Boolean, default: false }
    },
    setup(i) {
      const t2 = i, o = vue.computed(() => t2.id !== null ? t2.id : "id_" + v4().toString().replace(/-/g, "")), n = vue.computed(() => {
        let e = "";
        return t2.placement === "right" && (e += "uu-sidebar-right "), t2.mobilePlacement === "bottom" && (e += "uu-sidebar-mobile-bottom "), t2.stickySidebar && (e += "uu-sidebar-sticky "), t2.mobileStickySidebar && (e += "uu-sidebar-mobile-sticky "), e;
      });
      return (e, l) => (vue.openBlock(), vue.createElementBlock("div", {
        class: vue.normalizeClass(["uu-sidebar-container", n.value])
      }, [
        vue.createElementVNode("aside", Me, [
          vue.createElementVNode("button", {
            class: "uu-sidebar-toggle",
            type: "button",
            "data-bs-toggle": "collapse",
            "data-bs-target": "#" + o.value,
            "aria-expanded": "false"
          }, [
            vue.renderSlot(e.$slots, "sidebar-button")
          ], 8, Te),
          vue.createElementVNode("div", {
            id: o.value,
            class: "uu-sidebar-collapse collapse"
          }, [
            vue.renderSlot(e.$slots, "sidebar")
          ], 8, qe)
        ]),
        vue.createElementVNode("div", Re, [
          vue.renderSlot(e.$slots, "default")
        ])
      ], 2));
    }
  }), Fe = { class: "uu-list-filter" }, Ze = { class: "uu-list-filter-label" }, Ge = {
    key: 2,
    class: "uu-list-filter-field"
  }, Qe = ["value"], We = /* @__PURE__ */ vue.defineComponent({
    __name: "Filter",
    props: {
      filter: {},
      value: {}
    },
    emits: ["update:value"],
    setup(i, { emit: t$1 }) {
      return (o, n) => (vue.openBlock(), vue.createElementBlock("div", Fe, [
        vue.createElementVNode("div", Ze, vue.toDisplayString(o.filter.label), 1),
        o.filter.type === "checkbox" ? (vue.openBlock(), vue.createBlock(vue.unref(Ue), {
          key: 0,
          options: o.filter.options ?? [],
          "model-value": o.value ?? [],
          "onUpdate:modelValue": n[0] || (n[0] = (e) => t$1("update:value", e))
        }, null, 8, ["options", "model-value"])) : vue.createCommentVNode("", true),
        o.filter.type === "radio" ? (vue.openBlock(), vue.createBlock(vue.unref(Ne), {
          key: 1,
          options: o.filter.options ?? [],
          "model-value": o.value ?? "",
          "onUpdate:modelValue": n[1] || (n[1] = (e) => t$1("update:value", e))
        }, null, 8, ["options", "model-value"])) : vue.createCommentVNode("", true),
        o.filter.type === "date" ? (vue.openBlock(), vue.createElementBlock("div", Ge, [
          vue.createElementVNode("input", {
            type: "date",
            value: o.value,
            class: "form-control",
            onInput: n[2] || (n[2] = (e) => t$1("update:value", vue.unref(t)(e)))
          }, null, 40, Qe)
        ])) : vue.createCommentVNode("", true)
      ]));
    }
  }), Ae = { key: 0 }, Y = /* @__PURE__ */ vue.defineComponent({
    __name: "FilterBar",
    props: {
      filters: {},
      filterValues: {}
    },
    emits: ["update:filter-values"],
    setup(i, { emit: t2 }) {
      const o = i;
      function n(e, l) {
        let a = { ...o.filterValues };
        a[e] = l, t2("update:filter-values", a);
      }
      return (e, l) => e.filters ? (vue.openBlock(), vue.createElementBlock("div", Ae, [
        (vue.openBlock(true), vue.createElementBlock(vue.Fragment, null, vue.renderList(e.filters, (a) => (vue.openBlock(), vue.createBlock(We, {
          key: a.field,
          filter: a,
          value: e.filterValues[a.field] ?? void 0,
          "onUpdate:value": (u) => n(a.field, u)
        }, null, 8, ["filter", "value", "onUpdate:value"]))), 128))
      ])) : vue.createCommentVNode("", true);
    }
  }), He = { class: "search" }, Je = ["value", "placeholder"], R = /* @__PURE__ */ vue.defineComponent({
    __name: "SearchControl",
    props: {
      modelValue: {}
    },
    emits: ["update:modelValue", "update:model-value"],
    setup(i, { emit: t$1 }) {
      function o(a, u = 500) {
        let _;
        return (...b) => {
          clearTimeout(_), _ = setTimeout(() => {
            a.apply(this, b);
          }, u);
        };
      }
      function n(a) {
        t$1("update:modelValue", a);
      }
      const e = o((a) => n(a)), { t: l } = useI18n();
      return (a, u) => (vue.openBlock(), vue.createElementBlock("div", He, [
        vue.createElementVNode("input", {
          id: "search",
          class: "form-control",
          value: a.modelValue,
          placeholder: vue.unref(l)("placeholder"),
          onInput: u[0] || (u[0] = (_) => vue.unref(e)(vue.unref(t)(_)))
        }, null, 40, Je)
      ]));
    }
  });
  function Q(i) {
    const t2 = i;
    t2.__i18n = t2.__i18n || [], t2.__i18n.push({
      locale: "",
      resource: {
        en: {
          placeholder: (o) => {
            const { normalize: n } = o;
            return n(["Search"]);
          }
        },
        nl: {
          placeholder: (o) => {
            const { normalize: n } = o;
            return n(["Zoeken"]);
          }
        }
      }
    });
  }
  typeof Q == "function" && Q(R);
  const Ke = ["value"], Xe = ["value"], x = /* @__PURE__ */ vue.defineComponent({
    __name: "PageSizeControl",
    props: {
      pageSize: {},
      pageSizeOptions: {}
    },
    emits: ["update:pageSize", "update:page-size"],
    setup(i, { emit: t$1 }) {
      const o = i;
      function n(e) {
        if (typeof e == "string")
          try {
            e = Number(e);
          } catch {
            e = o.pageSizeOptions[0] ?? 10;
          }
        t$1("update:pageSize", e);
      }
      return (e, l) => (vue.openBlock(), vue.createElementBlock("select", {
        value: e.pageSize,
        class: "form-select",
        onChange: l[0] || (l[0] = (a) => n(vue.unref(t)(a)))
      }, [
        (vue.openBlock(true), vue.createElementBlock(vue.Fragment, null, vue.renderList(e.pageSizeOptions, (a) => (vue.openBlock(), vue.createElementBlock("option", {
          key: a,
          value: a
        }, vue.toDisplayString(a), 9, Xe))), 128))
      ], 40, Ke));
    }
  }), Ye = ["value"], xe = ["value"], ee = /* @__PURE__ */ vue.defineComponent({
    __name: "SortControl",
    props: {
      currentSort: {},
      sortOptions: {}
    },
    emits: ["update:current-sort", "update:currentSort"],
    setup(i, { emit: t$1 }) {
      return (o, n) => (vue.openBlock(), vue.createElementBlock("select", {
        value: o.currentSort,
        class: "form-select",
        onChange: n[0] || (n[0] = (e) => o.$emit("update:current-sort", vue.unref(t)(e).trim()))
      }, [
        (vue.openBlock(true), vue.createElementBlock(vue.Fragment, null, vue.renderList(o.sortOptions, ({ field: e, label: l }) => (vue.openBlock(), vue.createElementBlock("option", {
          key: e,
          value: e
        }, vue.toDisplayString(l), 9, xe))), 128))
      ], 40, Ye));
    }
  }), et = { key: 0 }, j = /* @__PURE__ */ vue.defineComponent({
    __name: "SearchResultNum",
    props: {
      searchQuery: {},
      pageNum: {},
      totalNum: {}
    },
    setup(i) {
      const { t: t2 } = useI18n();
      return (o, n) => (vue.openBlock(), vue.createElementBlock("div", null, [
        o.searchQuery ? (vue.openBlock(), vue.createElementBlock("span", et, vue.toDisplayString(vue.unref(t2)("search", { query: o.searchQuery })), 1)) : vue.createCommentVNode("", true),
        vue.createTextVNode(" " + vue.toDisplayString(vue.unref(t2)("showing", {
          pageNum: o.pageNum,
          totalNum: Intl.NumberFormat().format(o.totalNum)
        })), 1)
      ]));
    }
  });
  function W(i) {
    const t2 = i;
    t2.__i18n = t2.__i18n || [], t2.__i18n.push({
      locale: "",
      resource: {
        en: {
          search: (o) => {
            const { normalize: n, interpolate: e, named: l } = o;
            return n(["Search result: ", e(l("query")), ","]);
          },
          showing: (o) => {
            const { normalize: n, interpolate: e, named: l } = o;
            return n(["showing ", e(l("pageNum")), " of ", e(l("totalNum")), " results"]);
          }
        },
        nl: {
          search: (o) => {
            const { normalize: n, interpolate: e, named: l } = o;
            return n(["Zoekresultaat: ", e(l("query")), ","]);
          },
          showing: (o) => {
            const { normalize: n, interpolate: e, named: l } = o;
            return n([e(l("pageNum")), " van ", e(l("totalNum")), " getoond"]);
          }
        }
      }
    });
  }
  typeof W == "function" && W(j);
  const tt = { class: "uu-container" }, nt = { class: "uu-list" }, ot = { class: "uu-list-controls" }, at = {
    key: 1,
    class: "uu-list-order-control"
  }, st = { class: "uu-list-page-size-control" }, lt = {
    key: 0,
    class: "uu-list-filters"
  }, rt = { class: "uu-list-content" }, it = /* @__PURE__ */ vue.defineComponent({
    __name: "Default",
    props: {
      data: {},
      isLoading: { type: Boolean },
      totalData: {},
      currentPage: {},
      searchEnabled: { type: Boolean },
      search: {},
      sortEnabled: { type: Boolean },
      currentSort: {},
      sortOptions: {},
      pageSize: {},
      pageSizeOptions: {},
      filtersEnabled: { type: Boolean },
      filters: {},
      filterValues: {}
    },
    emits: ["update:current-page", "update:search", "update:current-sort", "update:page-size", "update:filter-values"],
    setup(i, { emit: t2 }) {
      const o = i, n = vue.computed(() => Math.ceil(o.totalData / o.pageSize));
      return (e, l) => {
        var a;
        return vue.openBlock(), vue.createElementBlock("div", tt, [
          vue.createElementVNode("div", nt, [
            vue.createElementVNode("div", ot, [
              e.searchEnabled ? (vue.openBlock(), vue.createBlock(R, {
                key: 0,
                "model-value": e.search,
                class: "uu-list-search-control",
                "onUpdate:modelValue": l[0] || (l[0] = (u) => e.$emit("update:search", u))
              }, null, 8, ["model-value"])) : vue.createCommentVNode("", true),
              vue.createVNode(j, {
                "search-query": e.search,
                "page-num": ((a = e.data) == null ? void 0 : a.length) ?? 0,
                "total-num": e.totalData,
                class: "uu-list-search-text-control"
              }, null, 8, ["search-query", "page-num", "total-num"]),
              e.sortEnabled ? (vue.openBlock(), vue.createElementBlock("div", at, [
                vue.createVNode(ee, {
                  "current-sort": e.currentSort,
                  "sort-options": e.sortOptions,
                  "onUpdate:currentSort": l[1] || (l[1] = (u) => t2("update:current-sort", u))
                }, null, 8, ["current-sort", "sort-options"])
              ])) : vue.createCommentVNode("", true),
              vue.createElementVNode("div", st, [
                vue.createVNode(x, {
                  "page-size-options": e.pageSizeOptions,
                  "page-size": e.pageSize,
                  "onUpdate:pageSize": l[2] || (l[2] = (u) => t2("update:page-size", u))
                }, null, 8, ["page-size-options", "page-size"])
              ])
            ]),
            e.filtersEnabled ? (vue.openBlock(), vue.createElementBlock("div", lt, [
              vue.createVNode(Y, {
                filters: e.filters,
                "filter-values": e.filterValues,
                "onUpdate:filterValues": l[3] || (l[3] = (u) => e.$emit("update:filter-values", u))
              }, null, 8, ["filters", "filter-values"])
            ])) : vue.createCommentVNode("", true),
            vue.createElementVNode("div", rt, [
              vue.renderSlot(e.$slots, "data", {
                data: e.data,
                isLoading: e.isLoading
              }),
              vue.createElementVNode("div", null, [
                e.data ? (vue.openBlock(), vue.createBlock(vue.unref(q), {
                  key: 0,
                  "max-pages": n.value,
                  currentpage: e.currentPage,
                  onChangePage: l[4] || (l[4] = (u) => e.$emit("update:current-page", u))
                }, null, 8, ["max-pages", "currentpage"])) : vue.createCommentVNode("", true)
              ])
            ])
          ])
        ]);
      };
    }
  }), ut = { class: "w-100 d-flex align-items-center gap-3 uu-list-controls" }, dt = {
    key: 0,
    class: "ms-auto"
  }, te = /* @__PURE__ */ vue.defineComponent({
    __name: "Sidebar",
    props: {
      data: {},
      isLoading: { type: Boolean },
      totalData: {},
      currentPage: {},
      searchEnabled: { type: Boolean },
      search: {},
      sortEnabled: { type: Boolean },
      currentSort: {},
      sortOptions: {},
      pageSize: {},
      pageSizeOptions: {},
      filtersEnabled: { type: Boolean },
      filters: {},
      filterValues: {}
    },
    emits: ["update:current-page", "update:search", "update:current-sort", "update:page-size", "update:filter-values"],
    setup(i, { emit: t2 }) {
      const o = i, n = vue.computed(() => Math.ceil(o.totalData / o.pageSize));
      return (e, l) => (vue.openBlock(), vue.createBlock(vue.unref(je), { class: "uu-list-sidebar" }, {
        sidebar: vue.withCtx(() => [
          e.searchEnabled ? (vue.openBlock(), vue.createBlock(R, {
            key: 0,
            "model-value": e.search,
            "onUpdate:modelValue": l[0] || (l[0] = (a) => e.$emit("update:search", a))
          }, null, 8, ["model-value"])) : vue.createCommentVNode("", true),
          e.filters ? (vue.openBlock(), vue.createBlock(Y, {
            key: 1,
            filters: e.filters,
            "filter-values": e.filterValues,
            "onUpdate:filterValues": l[1] || (l[1] = (a) => e.$emit("update:filter-values", a))
          }, null, 8, ["filters", "filter-values"])) : vue.createCommentVNode("", true)
        ]),
        default: vue.withCtx(() => {
          var a;
          return [
            vue.createElementVNode("div", null, [
              vue.createElementVNode("div", ut, [
                vue.createVNode(j, {
                  "search-query": e.search,
                  "page-num": ((a = e.data) == null ? void 0 : a.length) ?? 0,
                  "total-num": e.totalData
                }, null, 8, ["search-query", "page-num", "total-num"]),
                e.sortEnabled ? (vue.openBlock(), vue.createElementBlock("div", dt, [
                  vue.createVNode(ee, {
                    "current-sort": e.currentSort,
                    "sort-options": e.sortOptions,
                    "onUpdate:currentSort": l[2] || (l[2] = (u) => t2("update:current-sort", u))
                  }, null, 8, ["current-sort", "sort-options"])
                ])) : vue.createCommentVNode("", true),
                vue.createElementVNode("div", null, [
                  vue.createVNode(x, {
                    "page-size-options": e.pageSizeOptions,
                    "page-size": e.pageSize,
                    "onUpdate:pageSize": l[3] || (l[3] = (u) => t2("update:page-size", u))
                  }, null, 8, ["page-size-options", "page-size"])
                ])
              ]),
              vue.renderSlot(e.$slots, "data", {
                data: e.data,
                isLoading: e.isLoading
              }),
              vue.createElementVNode("div", null, [
                e.data ? (vue.openBlock(), vue.createBlock(vue.unref(q), {
                  key: 0,
                  "max-pages": n.value,
                  currentpage: e.currentPage,
                  onChangePage: l[4] || (l[4] = (u) => e.$emit("update:current-page", u))
                }, null, 8, ["max-pages", "currentpage"])) : vue.createCommentVNode("", true)
              ])
            ])
          ];
        }),
        _: 3
      }));
    }
  });
  function A(i) {
    const t2 = i;
    t2.__i18n = t2.__i18n || [], t2.__i18n.push({
      locale: "",
      resource: {
        en: {
          loading: (o) => {
            const { normalize: n } = o;
            return n(["Loading...."]);
          },
          no_data: (o) => {
            const { normalize: n } = o;
            return n(["No items to display"]);
          }
        },
        nl: {
          loading: (o) => {
            const { normalize: n } = o;
            return n(["Gegevens worden laden..."]);
          },
          no_data: (o) => {
            const { normalize: n } = o;
            return n(["Geen gegevens om te tonen"]);
          }
        }
      }
    });
  }
  typeof A == "function" && A(te);
  const pt = /* @__PURE__ */ vue.defineComponent({
    __name: "DebugVisualizer",
    props: {
      data: {},
      isLoading: { type: Boolean, default: false }
    },
    setup(i) {
      return (t2, o) => (vue.openBlock(), vue.createElementBlock("pre", null, vue.toDisplayString(t2.data), 1));
    }
  }), ct = /* @__PURE__ */ vue.defineComponent({
    __name: "UUList",
    props: {
      container: { default: "default" },
      data: {},
      isLoading: { type: Boolean, default: false },
      totalData: {},
      currentPage: {},
      searchEnabled: { type: Boolean, default: false },
      search: { default: "" },
      sortEnabled: { type: Boolean, default: false },
      currentSort: { default: "" },
      sortOptions: { default: () => [] },
      pageSize: { default: 10 },
      pageSizeOptions: { default: () => [10, 25, 50] },
      filtersEnabled: { type: Boolean, default: false },
      filters: {},
      filterValues: {}
    },
    emits: ["update:current-page", "update:search", "update:current-sort", "update:page-size", "update:filter-values"],
    setup(i, { emit: t2 }) {
      const o = i, n = vue.computed(() => {
        switch (o.container) {
          case "default":
            return it;
          case "sidebar":
            return te;
        }
      });
      return (e, l) => (vue.openBlock(), vue.createBlock(vue.resolveDynamicComponent(n.value), {
        "is-loading": e.isLoading,
        data: e.data,
        "total-data": e.totalData,
        "search-enabled": e.searchEnabled,
        search: e.search,
        "sort-enabled": e.sortEnabled,
        "current-sort": e.currentSort,
        "current-page": e.currentPage,
        "page-size-options": e.pageSizeOptions,
        "sort-options": e.sortOptions,
        "page-size": e.pageSize,
        "filters-enabled": e.filtersEnabled,
        filters: e.filters,
        "filter-values": e.filterValues,
        "onUpdate:search": l[0] || (l[0] = (a) => t2("update:search", a)),
        "onUpdate:currentSort": l[1] || (l[1] = (a) => t2("update:current-sort", a)),
        "onUpdate:pageSize": l[2] || (l[2] = (a) => t2("update:page-size", a)),
        "onUpdate:currentPage": l[3] || (l[3] = (a) => t2("update:current-page", a)),
        "onUpdate:filterValues": l[4] || (l[4] = (a) => t2("update:filter-values", a))
      }, {
        data: vue.withCtx(({ data: a, isLoading: u }) => [
          vue.renderSlot(e.$slots, "data", {
            data: a,
            isLoading: u
          }, () => [
            vue.createVNode(pt, {
              data: a,
              "is-loading": u
            }, null, 8, ["data", "is-loading"])
          ])
        ]),
        _: 3
      }, 40, ["is-loading", "data", "total-data", "search-enabled", "search", "sort-enabled", "current-sort", "current-page", "page-size-options", "sort-options", "page-size", "filters-enabled", "filters", "filter-values"]));
    }
  }), mt = /* @__PURE__ */ vue.defineComponent({
    __name: "DDVString",
    props: {
      item: {},
      column: {}
    },
    setup(i) {
      return (t2, o) => (vue.openBlock(), vue.createElementBlock("span", {
        class: vue.normalizeClass(t2.column.classes)
      }, vue.toDisplayString(t2.item[t2.column.field]), 3));
    }
  }), ft = /* @__PURE__ */ vue.defineComponent({
    __name: "DDVDate",
    props: {
      item: {},
      column: {}
    },
    setup(i) {
      const t2 = i, o = vue.computed(() => {
        let n = null;
        try {
          n = new Date(t2.item[t2.column.field]);
        } catch (a) {
          return console.error(a), "";
        }
        let e;
        if (t2.column.language !== void 0 && t2.column.language !== null && (e = t2.column.language), typeof t2.column.format == "string") {
          let a = null;
          switch (t2.column.format) {
            case "date":
              a = {
                dateStyle: "medium"
              };
              break;
            case "time":
              a = {
                timeStyle: "short"
              };
              break;
            case "datetime":
              a = {
                dateStyle: "medium",
                timeStyle: "short"
              };
              break;
          }
          return new Intl.DateTimeFormat(e, a).format(n);
        }
        return typeof t2.column.format == "object" && t2.column.format !== null ? new Intl.DateTimeFormat(
          e,
          t2.column.format
        ).format(n) : new Intl.DateTimeFormat(e).format(n);
      });
      return (n, e) => (vue.openBlock(), vue.createElementBlock("span", {
        class: vue.normalizeClass(n.column.classes)
      }, vue.toDisplayString(o.value), 3));
    }
  }), gt = { key: 0 }, ht = /* @__PURE__ */ vue.defineComponent({
    __name: "DDVButton",
    props: {
      item: {},
      column: {}
    },
    setup(i) {
      return (t2, o) => t2.item[t2.column.field] ? (vue.openBlock(), vue.createElementBlock("span", gt, [
        vue.createVNode(vue.unref(X), {
          href: t2.item[t2.column.field].link,
          "css-classes": t2.item[t2.column.field].classes,
          "new-tab": t2.item[t2.column.field].new_tab,
          size: t2.column.size,
          variant: t2.column.variant
        }, {
          default: vue.withCtx(() => [
            vue.createTextVNode(vue.toDisplayString(t2.item[t2.column.field].text), 1)
          ]),
          _: 1
        }, 8, ["href", "css-classes", "new-tab", "size", "variant"])
      ])) : vue.createCommentVNode("", true);
    }
  }), vt = { key: 0 }, bt = ["href", "target"], _t = /* @__PURE__ */ vue.defineComponent({
    __name: "DDVLink",
    props: {
      item: {},
      column: {}
    },
    setup(i) {
      return (t2, o) => t2.item[t2.column.field] ? (vue.openBlock(), vue.createElementBlock("span", vt, [
        vue.createElementVNode("a", {
          href: t2.item[t2.column.field].link,
          class: vue.normalizeClass(t2.column.classes),
          target: t2.item[t2.column.field].new_tab ? "_blank" : "_self"
        }, vue.toDisplayString(t2.item[t2.column.field].text), 11, bt)
      ])) : vue.createCommentVNode("", true);
    }
  }), yt = ["innerHTML"], $t = /* @__PURE__ */ vue.defineComponent({
    __name: "DDVHTML",
    props: {
      item: {},
      column: {}
    },
    setup(i) {
      return (t2, o) => (vue.openBlock(), vue.createElementBlock("span", {
        innerHTML: t2.item[t2.column.field]
      }, null, 8, yt));
    }
  }), kt = {
    key: 0,
    class: "dropdown"
  }, zt = /* @__PURE__ */ vue.createStaticVNode('<button class="btn p-1" type="button" data-bs-toggle="dropdown" aria-expanded="false" style="line-height:1rem;"><svg width="16px" height="16px" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="M12 13.75C12.9665 13.75 13.75 12.9665 13.75 12C13.75 11.0335 12.9665 10.25 12 10.25C11.0335 10.25 10.25 11.0335 10.25 12C10.25 12.9665 11.0335 13.75 12 13.75Z" fill="#000000"></path><path d="M19 13.75C19.9665 13.75 20.75 12.9665 20.75 12C20.75 11.0335 19.9665 10.25 19 10.25C18.0335 10.25 17.25 11.0335 17.25 12C17.25 12.9665 18.0335 13.75 19 13.75Z" fill="#000000"></path><path d="M5 13.75C5.9665 13.75 6.75 12.9665 6.75 12C6.75 11.0335 5.9665 10.25 5 10.25C4.0335 10.25 3.25 11.0335 3.25 12C3.25 12.9665 4.0335 13.75 5 13.75Z" fill="#000000"></path></svg></button>', 1), St = { class: "dropdown-menu" }, wt = {
    key: 0,
    class: "dropdown-divider"
  }, Ct = ["href", "target"], Bt = /* @__PURE__ */ vue.defineComponent({
    __name: "DDVActions",
    props: {
      item: {},
      column: {}
    },
    setup(i) {
      const t2 = i, o = vue.computed(() => t2.item[t2.column.field].entries());
      return (n, e) => o.value ? (vue.openBlock(), vue.createElementBlock("div", kt, [
        zt,
        vue.createElementVNode("ul", St, [
          (vue.openBlock(true), vue.createElementBlock(vue.Fragment, null, vue.renderList(o.value, ([l, a]) => (vue.openBlock(), vue.createElementBlock("li", { key: l }, [
            a.divider ? (vue.openBlock(), vue.createElementBlock("hr", wt)) : (vue.openBlock(), vue.createElementBlock("a", {
              key: 1,
              href: a.link,
              class: vue.normalizeClass(["dropdown-item", a.classes ?? ""]),
              target: a.new_tab ? "_blank" : "_self"
            }, vue.toDisplayString(a.text), 11, Ct))
          ]))), 128))
        ])
      ])) : vue.createCommentVNode("", true);
    }
  }), Vt = /* @__PURE__ */ vue.defineComponent({
    __name: "DDVColumn",
    props: {
      item: {},
      column: {}
    },
    setup(i) {
      return (t2, o) => t2.column.type == "string" ? (vue.openBlock(), vue.createBlock(mt, {
        key: 0,
        item: t2.item,
        column: t2.column
      }, null, 8, ["item", "column"])) : t2.column.type == "date" ? (vue.openBlock(), vue.createBlock(ft, {
        key: 1,
        item: t2.item,
        column: t2.column
      }, null, 8, ["item", "column"])) : t2.column.type == "button" ? (vue.openBlock(), vue.createBlock(ht, {
        key: 2,
        item: t2.item,
        column: t2.column
      }, null, 8, ["item", "column"])) : t2.column.type == "link" ? (vue.openBlock(), vue.createBlock(_t, {
        key: 3,
        item: t2.item,
        column: t2.column
      }, null, 8, ["item", "column"])) : t2.column.type == "html" ? (vue.openBlock(), vue.createBlock($t, {
        key: 4,
        item: t2.item,
        column: t2.column
      }, null, 8, ["item", "column"])) : t2.column.type == "actions" ? (vue.openBlock(), vue.createBlock(Bt, {
        key: 5,
        item: t2.item,
        column: t2.column
      }, null, 8, ["item", "column"])) : vue.createCommentVNode("", true);
    }
  }), Dt = /* @__PURE__ */ vue.defineComponent({
    __name: "DDVRow",
    props: {
      item: {},
      columns: {}
    },
    setup(i) {
      return (t2, o) => (vue.openBlock(), vue.createElementBlock("tr", null, [
        (vue.openBlock(true), vue.createElementBlock(vue.Fragment, null, vue.renderList(t2.columns, (n) => (vue.openBlock(), vue.createElementBlock("td", {
          key: n.field,
          class: "align-middle"
        }, [
          vue.createVNode(Vt, {
            column: n,
            item: t2.item
          }, null, 8, ["column", "item"])
        ]))), 128))
      ]));
    }
  }), Ut = {
    key: 0,
    class: "alert alert-info w-100"
  }, Ot = { key: 0 }, It = { key: 1 }, Pt = ["colspan"], ne = /* @__PURE__ */ vue.defineComponent({
    __name: "DataDefinedVisualizer",
    props: {
      data: { default: null },
      columns: {},
      isLoading: { type: Boolean, default: false }
    },
    setup(i) {
      const t2 = i, o = vue.computed(() => t2.data === null || t2.data === void 0 || t2.data.length === 0), { t: n } = useI18n();
      return (e, l) => e.isLoading && o.value ? (vue.openBlock(), vue.createElementBlock("div", Ut, vue.toDisplayString(vue.unref(n)("loading")), 1)) : (vue.openBlock(), vue.createElementBlock("table", {
        key: 1,
        class: vue.normalizeClass(["table", e.isLoading ? "loading" : ""])
      }, [
        vue.createElementVNode("thead", null, [
          vue.createElementVNode("tr", null, [
            (vue.openBlock(true), vue.createElementBlock(vue.Fragment, null, vue.renderList(e.columns, (a) => (vue.openBlock(), vue.createElementBlock("th", {
              key: a.field
            }, vue.toDisplayString(a.label), 1))), 128))
          ])
        ]),
        o.value ? (vue.openBlock(), vue.createElementBlock("tbody", It, [
          vue.createElementVNode("tr", null, [
            vue.createElementVNode("td", {
              colspan: e.columns.length
            }, vue.toDisplayString(vue.unref(n)("no_data")), 9, Pt)
          ])
        ])) : (vue.openBlock(), vue.createElementBlock("tbody", Ot, [
          (vue.openBlock(true), vue.createElementBlock(vue.Fragment, null, vue.renderList(e.data, (a) => (vue.openBlock(), vue.createBlock(Dt, {
            key: a.id,
            item: a,
            columns: e.columns
          }, null, 8, ["item", "columns"]))), 128))
        ]))
      ], 2));
    }
  });
  function H(i) {
    const t2 = i;
    t2.__i18n = t2.__i18n || [], t2.__i18n.push({
      locale: "",
      resource: {
        en: {
          loading: (o) => {
            const { normalize: n } = o;
            return n(["Loading...."]);
          },
          no_data: (o) => {
            const { normalize: n } = o;
            return n(["No items to display"]);
          }
        },
        nl: {
          loading: (o) => {
            const { normalize: n } = o;
            return n(["Gegevens worden laden..."]);
          },
          no_data: (o) => {
            const { normalize: n } = o;
            return n(["Geen gegevens om te tonen"]);
          }
        }
      }
    });
  }
  typeof H == "function" && H(ne);
  const Ft = /* @__PURE__ */ vue.defineComponent({
    __name: "DSCList",
    props: {
      config: {}
    },
    setup(i) {
      const t2 = i, o = vue.ref(t2.config.pageSize), n = vue.ref(1), e = vue.ref(""), l = vue.ref("id"), a = vue.ref(true);
      function u() {
        var f;
        let p = {};
        return (f = t2.config.filters) == null || f.forEach(($) => {
          var O;
          if ($.initial) {
            p[$.field] = $.initial;
            return;
          }
          switch ($.type) {
            case "date":
              p[$.field] = null;
              break;
            case "checkbox":
              p[$.field] = [];
              break;
            case "radio":
              ((O = $.options) == null ? void 0 : O.length) != 0 && $.options && (p[$.field] = $.options[0][0]);
              break;
          }
        }), p;
      }
      const _ = vue.ref(u());
      let b = vue.ref(null);
      const E = vue.computed(() => {
        let p = [];
        p.push("page_size=" + encodeURIComponent(o.value));
        for (const [f, $] of Object.entries(_.value))
          $ != null && (typeof $ == "object" ? $.forEach(
            (O) => p.push(f + "=" + encodeURIComponent(O))
          ) : p.push(f + "=" + encodeURIComponent($)));
        return e.value && p.push("search=" + encodeURIComponent(e.value)), p.push("ordering=" + encodeURIComponent(l.value)), n.value = 1, p;
      }), P = vue.computed(() => {
        let p = E.value, f = "page=" + encodeURIComponent(n.value);
        return p.length !== 0 && (f = "&" + f), "?" + p.join("&") + f;
      }), D = vue.computed(() => {
        let p = new URL(window.location.protocol + "//" + window.location.host);
        return p.pathname = t2.config.dataUri, p.search = P.value, console.log(p.toString()), p.toString();
      });
      vue.watch(D, () => {
        F();
      });
      const y = vue.ref(null);
      function F() {
        y.value && y.value.abort(), y.value = new AbortController(), a.value = true, fetch(D.value, { signal: y.value.signal }).then((p) => {
          p.json().then((f) => {
            b.value = f, a.value = false, y.value = null;
          });
        }).catch((p) => {
          console.log(p);
        });
      }
      return vue.onMounted(() => {
        F();
      }), (p, f) => {
        var $, O, Z;
        return vue.openBlock(), vue.createBlock(ct, {
          "is-loading": a.value,
          data: (($ = vue.unref(b)) == null ? void 0 : $.results) ?? void 0,
          "total-data": ((O = vue.unref(b)) == null ? void 0 : O.count) ?? 0,
          "search-enabled": p.config.searchEnabled,
          search: e.value,
          "sort-enabled": p.config.sortEnabled,
          "current-sort": l.value,
          "page-size-options": p.config.pageSizeOptions,
          "sort-options": p.config.sortOptions ?? [],
          "page-size": ((Z = vue.unref(b)) == null ? void 0 : Z.page_size) ?? 10,
          "current-page": n.value,
          "filters-enabled": p.config.filtersEnabled,
          filters: p.config.filters ?? [],
          "filter-values": _.value,
          container: p.config.container,
          "onUpdate:search": f[0] || (f[0] = (C) => e.value = C),
          "onUpdate:currentSort": f[1] || (f[1] = (C) => l.value = C),
          "onUpdate:pageSize": f[2] || (f[2] = (C) => o.value = C),
          "onUpdate:currentPage": f[3] || (f[3] = (C) => n.value = C),
          "onUpdate:filterValues": f[4] || (f[4] = (C) => _.value = C)
        }, {
          data: vue.withCtx(({ data: C, isLoading: oe }) => [
            vue.createVNode(ne, {
              data: C,
              columns: p.config.columns,
              "is-loading": oe
            }, null, 8, ["data", "columns", "is-loading"])
          ]),
          _: 1
        }, 8, ["is-loading", "data", "total-data", "search-enabled", "search", "sort-enabled", "current-sort", "page-size-options", "sort-options", "page-size", "current-page", "filters-enabled", "filters", "filter-values", "container"]);
      };
    }
  });
  const style = "";
  return Ft;
}(Vue);
