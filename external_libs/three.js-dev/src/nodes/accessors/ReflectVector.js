import { cameraViewMatrix } from './Camera.js';
import { normalView } from './Normal.js';
import { positionViewDirection } from './Position.js';
import { materialRefractionRatio } from './MaterialProperties.js';

/**
 * The reflect vector in view space.
 *
 * @tsl
 * @type {Node<vec3>}
 */
export const reflectView = /*@__PURE__*/ positionViewDirection.negate().reflect( normalView );

/**
 * The refract vector in view space.
 *
 * @tsl
 * @type {Node<vec3>}
 */
export const refractView = /*@__PURE__*/ positionViewDirection.negate().refract( normalView, materialRefractionRatio );

/**
 * Used for sampling cube maps when using cube reflection mapping.
 *
 * @tsl
 * @type {Node<vec3>}
 */
export const reflectVector = /*@__PURE__*/ reflectView.transformDirection( cameraViewMatrix ).toVar( 'reflectVector' );

/**
 * Used for sampling cube maps when using cube refraction mapping.
 *
 * @tsl
 * @type {Node<vec3>}
 */
export const refractVector = /*@__PURE__*/ refractView.transformDirection( cameraViewMatrix ).toVar( 'reflectVector' );
